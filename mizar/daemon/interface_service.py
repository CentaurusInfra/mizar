import logging
import sys
import os
import subprocess
from mizar.proto.interface_pb2 import *
from mizar.proto.interface_pb2_grpc import InterfaceServiceServicer, InterfaceServiceStub
import time
import grpc
import json
import fs
import uuid
from mizar.common.common import *
from logging.handlers import SysLogHandler
from concurrent import futures
import threading
from google.protobuf import empty_pb2
from mizar.common.rpc import TrnRpc
from mizar.common.constants import *
from pyroute2 import IPRoute, NetNS
import queue

logger = logging.getLogger('mizar_interface_service')
handler = SysLogHandler(address='/dev/log')
logger.addHandler(handler)
logger = logging.getLogger()

CONSUME_INTERFACE_TIMEOUT = 5


class InterfaceServer(InterfaceServiceServicer):

    def __init__(self):
        self.interfaces_q = queue.Queue()
        self.iproute = IPRoute()
        self.interfaces = {}
        self.queued_pods = set()
        self.interfaces_lock = threading.Lock()

        cmd = 'ip addr show eth0 | grep "inet\\b" | awk \'{print $2}\' | cut -d/ -f1'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.droplet_ip = r.stdout.read().decode().strip()

        cmd = 'ip addr show eth0 | grep "link/ether\\b" | awk \'{print $2}\' | cut -d/ -f1'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.droplet_mac = r.stdout.read().decode().strip()

        cmd = 'hostname'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.droplet_name = r.stdout.read().decode().strip()

        self.itf = 'eth0'
        self.rpc = LocalTransitRpc('127.0.0.1', self.droplet_mac)

    def __del__(self):
        self.iproute.close()

    def InitializeInterfaces(self, request, context):
        interfaces = request
        for interface in interfaces.interfaces:
            self._CreateInterface(interface)
            logger.debug("Allocated mac {}".format(interface.address.mac))
        return interfaces

    def _CreateInterface(self, interface):
        if interface.interface_type == InterfaceType.veth:
            return self._CreateVethInterface(interface)

    def _CreateVethInterface(self, interface):
        veth_name = interface.veth.name
        veth_peer = interface.veth.peer

        veth_index = get_iface_index(veth_name, self.iproute)

        if veth_index == -1:
            self.iproute.link('add', ifname=veth_name,
                              peer=veth_peer, kind='veth')
            veth_index = get_iface_index(veth_name, self.iproute)

        address = InterfaceAddress(
            version=interface.address.version,
            ip_address=interface.address.ip_address,
            ip_prefix=interface.address.ip_prefix,
            gateway_ip=interface.address.gateway_ip,
            mac=get_iface_mac(veth_index, self.iproute),
            tunnel_id=interface.address.tunnel_id
        )
        interface.address.CopyFrom(address)

    def ProduceInterfaces(self, request, context):
        interfaces = request
        for interface in interfaces.interfaces:
            self._QueueInterface(interface)
        return interfaces

    def _QueueInterface(self, interface):
        pod_name = get_pod_name(interface.interface_id.pod_id)
        logger.info("Producing interface {}".format(interface))
        with self.interfaces_lock:
            if pod_name not in self.interfaces:
                self.interfaces[pod_name] = []
            self.interfaces[pod_name].append(interface)

            if pod_name not in self.queued_pods:
                self.interfaces_q.put(pod_name)
                self.queued_pods.add(pod_name)

        interface.status = InterfaceStatus.queued

    def _ConsumeInterfaces(self, pod_name, cni_params):
        with self.interfaces_lock:
            if pod_name in self.queued_pods:
                self.queued_pods.remove(pod_name)
            interfaces = self.interfaces.get(pod_name, [])
            for interface in interfaces:
                if interface.status == InterfaceStatus.queued:
                    self._ProvisionInterface(interface, cni_params)
                    interface.status = InterfaceStatus.consumed

        interfaces = InterfacesList(interfaces=interfaces)
        logger.info("Consumed {}".format(interfaces))
        return interfaces

    def _ProvisionInterface(self, interface, cni_params):
        if interface.interface_type == InterfaceType.veth:
            self._ProvisionVethInterface(interface, cni_params)

    def _ProvisionVethInterface(self, interface, cni_params):
        # Finalize all interface configuration. All main interface configuration
        # will be in the CNI. All the peer interface configuration, will be here
        # Network namespace operations (Move these to the CNI)

        veth_peer_index = get_iface_index(interface.veth.peer, self.iproute)
        self.iproute.link('set', index=veth_peer_index, state='up', mtu=9000)

        # Configure the Transit Agent
        self._ConfigureTrasitAgent(interface)

    def _ConfigureTrasitAgent(self, interface):
        self.rpc.load_transit_agent_xdp(interface)

        for bouncer in interface.bouncers:
            self.rpc.update_agent_substrate_ep(
                interface.veth.peer, bouncer.ip_address, bouncer.mac)

        self.rpc.update_agent_metadata(interface)
        self.rpc.update_ep(interface)

    def ConsumeInterfaces(self, request, context):
        cni_params = request
        requested_pod_id = cni_params.pod_id
        requested_pod_name = get_pod_name(requested_pod_id)
        logger.info("Consume Interfaces {}".format(request))
        logger.debug(
            "Consuming interfaces for pod {}".format(requested_pod_name))
        start = time.time()

        # The following is a synchronization mechanism to make sure the
        # CNI calls _ConsumeInterfaces after the interfaces got produced.
        # In Arktos, this may be skipped because the Kubelet will only
        # invoke CNI after the Pod operator marks the pod's network ready

        while True:
            try:
                queued_pod_name = self.interfaces_q.get(
                    timeout=CONSUME_INTERFACE_TIMEOUT)
            except:
                break

            if queued_pod_name == requested_pod_name:
                return self._ConsumeInterfaces(queued_pod_name, cni_params)

            self.interfaces_q.put(queued_pod_name)
            now = time.time()

            if now - start >= CONSUME_INTERFACE_TIMEOUT:
                break

        return self._ConsumeInterfaces(requested_pod_name, cni_params)

    def DeleteInterface(self, request, context):
        # NOOP for now
        return empty_pb2.Empty()


class InterfaceServiceClient():
    def __init__(self, ip):
        self.channel = grpc.insecure_channel('{}:50051'.format(ip))
        self.stub = InterfaceServiceStub(self.channel)

    def InitializeInterfaces(self, interfaces_list):
        resp = self.stub.InitializeInterfaces(interfaces_list)
        return resp

    def ProduceInterfaces(self, interfaces_list):
        resp = self.stub.ProduceInterfaces(interfaces_list)
        return resp

    def ConsumeInterfaces(self, pod_id):
        resp = self.stub.ConsumeInterfaces(pod_id)
        return resp

    def DeleteInterface(self, interface_id):
        resp = self.stub.DeleteInterface(interface_id)
        return resp


class LocalTransitRpc:
    def __init__(self, ip, mac, itf='eth0', benchmark=False):
        self.ip = ip
        self.mac = mac
        self.phy_itf = itf

        # transitd cli commands
        self.trn_cli = f'''nsenter -t 1 -m -u -n -i /trn_bin/transit -s {self.ip} '''
        self.trn_cli_load_transit_xdp = f'''{self.trn_cli} load-transit-xdp -i {self.phy_itf} -j'''
        self.trn_cli_unload_transit_xdp = f'''{self.trn_cli} unload-transit-xdp -i {self.phy_itf} -j'''
        self.trn_cli_update_vpc = f'''{self.trn_cli} update-vpc -i {self.phy_itf} -j'''
        self.trn_cli_get_vpc = f'''{self.trn_cli} get-vpc -i {self.phy_itf} -j'''
        self.trn_cli_delete_vpc = f'''{self.trn_cli} delete-vpc -i {self.phy_itf} -j'''
        self.trn_cli_update_net = f'''{self.trn_cli} update-net -i {self.phy_itf} -j'''
        self.trn_cli_get_net = f'''{self.trn_cli} get-net -i {self.phy_itf} -j'''
        self.trn_cli_delete_net = f'''{self.trn_cli} delete-net -i {self.phy_itf} -j'''
        self.trn_cli_update_ep = f'''{self.trn_cli} update-ep -i {self.phy_itf} -j'''
        self.trn_cli_get_ep = f'''{self.trn_cli} get-ep -i {self.phy_itf} -j'''
        self.trn_cli_delete_ep = f'''{self.trn_cli} delete-ep -i {self.phy_itf} -j'''
        self.trn_cli_load_pipeline_stage = f'''{self.trn_cli} load-pipeline-stage -i {self.phy_itf} -j'''
        self.trn_cli_unload_pipeline_stage = f'''{self.trn_cli} unload-pipeline-stage -i {self.phy_itf} -j'''

        self.trn_cli_load_transit_agent_xdp = f'''{self.trn_cli} load-agent-xdp'''
        self.trn_cli_unload_transit_agent_xdp = f'''{self.trn_cli} unload-agent-xdp'''
        self.trn_cli_update_agent_metadata = f'''{self.trn_cli} update-agent-metadata'''
        self.trn_cli_get_agent_metadata = f'''{self.trn_cli} get-agent-metadata'''
        self.trn_cli_delete_agent_metadata = f'''{self.trn_cli} delete-agent-metadata'''
        self.trn_cli_update_agent_ep = f'''{self.trn_cli} update-agent-ep'''
        self.trn_cli_get_agent_ep = f'''{self.trn_cli} get-agent-ep'''
        self.trn_cli_delete_agent_ep = f'''{self.trn_cli} delete-agent-ep'''

        if benchmark:
            self.xdp_path = "/trn_xdp/trn_transit_xdp_ebpf.o"
            self.agent_xdp_path = "/trn_xdp/trn_agent_xdp_ebpf.o"
        else:
            self.xdp_path = "/trn_xdp/trn_transit_xdp_ebpf_debug.o"
            self.agent_xdp_path = "/trn_xdp/trn_agent_xdp_ebpf_debug.o"

    def get_substrate_ep_json(self, ip, mac):
        jsonconf = {
            "tunnel_id": "0",
            "ip": ip,
            "eptype": "0",
            "mac": mac,
            "veth": "",
            "remote_ips": [""],
            "hosted_iface": ""
        }
        jsonconf = json.dumps(jsonconf)
        return jsonconf

    def load_transit_agent_xdp(self, interface):
        itf = interface.veth.peer
        agent_pcap_file = itf + '.pcap'
        jsonconf = {
            "xdp_path": self.agent_xdp_path,
            "pcapfile": agent_pcap_file
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_load_transit_agent_xdp} -i \'{itf}\' -j \'{jsonconf}\' '''
        logger.info("load_transit_agent_xdp: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info(
            "load_transit_agent_xdp returns {} {}".format(returncode, text))

    def update_ep(self, interface):
        peer = interface.veth.peer
        droplet_ip = interface.droplet.ip_address
        jsonconf = {
            "tunnel_id": interface.address.tunnel_id,
            "ip": interface.address.ip_address,
            "eptype": str(CONSTANTS.TRAN_SIMPLE_EP),
            "mac": interface.address.mac,
            "veth": interface.veth.name,
            "remote_ips": [droplet_ip],
            "hosted_iface": peer
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_update_ep} \'{jsonconf}\''''
        logger.info("update_ep: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info("returns {} {}".format(returncode, text))

    def update_agent_substrate_ep(self, veth_peer, ip, mac):
        itf = veth_peer
        jsonconf = self.get_substrate_ep_json(ip, mac)
        cmd = f'''{self.trn_cli_update_agent_ep} -i \'{itf}\' -j \'{jsonconf}\''''
        logger.info("update_agent_substrate_ep: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info(
            "update_agent_substrate_ep returns {} {}".format(returncode, text))

    def update_agent_metadata(self, interface):
        itf = interface.veth.peer
        bouncers = []
        for bouncer in interface.bouncers:
            bouncers.append(bouncer.ip_address)
        jsonconf = {
            "ep": {
                "tunnel_id": interface.address.tunnel_id,
                "ip": interface.address.ip_address,
                "eptype": str(CONSTANTS.TRAN_SIMPLE_EP),
                "mac": interface.address.mac,
                "veth": interface.veth.name,
                "remote_ips": [interface.droplet.ip_address],
                "hosted_iface": 'eth0'
            },
            "net": {
                "tunnel_id": interface.address.tunnel_id,
                "nip":  interface.address.gateway_ip,
                "prefixlen":  interface.address.ip_prefix,
                "switches_ips": bouncers
            },
            "eth": {
                "ip": interface.droplet.ip_address,
                "mac": interface.droplet.mac,
                "iface": 'eth0'
            }
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_update_agent_metadata} -i \'{itf}\' -j \'{jsonconf}\''''
        logger.info("update_agent_metadata: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info(
            "update_agent_metadata returns {} {}".format(returncode, text))

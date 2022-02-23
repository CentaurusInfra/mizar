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
import ipaddress

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('mizar_interface_service')
handler = SysLogHandler(address='/dev/log')
logger.addHandler(handler)
logger = logging.getLogger()

CONSUME_INTERFACE_TIMEOUT = 5
WAITING_SLEEP_INTERVAL = 0.5


class InterfaceServer(InterfaceServiceServicer):

    def __init__(self):
        self.iproute = IPRoute()
        self.interfaces = {}  # In-memory tracking for Pod interfaces
        self.pod_dict = {}

        self.itf = get_itf()
        cmd = 'ip addr show ' + \
            f'''{self.itf}''' + \
            ' | grep "inet\\b" | awk \'{print $2}\' | cut -d/ -f1'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.droplet_ip = r.stdout.read().decode().strip()

        cmd = 'ip addr show ' + \
            f'''{self.itf}''' + \
            ' | grep "link/ether\\b" | awk \'{print $2}\' | cut -d/ -f1'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.droplet_mac = r.stdout.read().decode().strip()

        cmd = 'hostname'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.droplet_name = r.stdout.read().decode().strip()

        self.rpc = LocalTransitRpc('127.0.0.1', self.droplet_mac, self.itf)

    def __del__(self):
        self.iproute.close()

    def InitializeInterfaces(self, request, context):
        """
        Called by the endpoints operator to initilaize the interface and
        allocate its mac address
        """
        interfaces = request
        for interface in interfaces.interfaces:
            self._CreateInterface(interface)
            logger.debug("Allocated mac {}".format(interface.address.mac))
        return interfaces

    def _CreateInterface(self, interface):
        """
        Type specific interface creation
        """
        if interface.interface_type == InterfaceType.veth:
            return self._CreateVethInterface(interface)

    def _CreateVethInterface(self, interface):
        """
        Creates a veth interface
        """
        veth_name = interface.veth.name
        veth_peer = interface.veth.peer
        veth_index = get_iface_index(veth_name, self.iproute)

        if veth_index == -1:
            logger.info("Creating interface {}".format(veth_name))
            self.iproute.link('add', ifname=veth_name,
                              peer=veth_peer, kind='veth')
            veth_index = get_iface_index(veth_name, self.iproute)
        else:
            logger.info("Interface {} already exists!".format(veth_name))

        # Update the mac address with the interface address
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
        """
        Called by the endpoints operator to program the transit Agent and
        prepare the interface for consumption.
        """
        interfaces = request
        for interface in interfaces.interfaces:
            self._QueueInterface(interface)
        return interfaces

    def _QueueInterface(self, interface):
        pod_name = get_pod_name(interface.interface_id.pod_id)
        logger.info("Producing interface {}".format(interface))
        logger.info("Current queued interfaces {}".format(self.interfaces))
        # Append the interface to the pod's interfaces (important in
        # multi-interfaces case)
        if pod_name not in self.interfaces:
            self.interfaces[pod_name] = []
        self.interfaces[pod_name].append(interface)

        # Move the pod_name into interfaces_q. This tells the consume
        # function that the pod has queued interfaces that can be consumed
        self.pod_dict[pod_name] = True

        # Change interface status from init to queued.
        interface.status = InterfaceStatus.queued

    def _ConsumeInterfaces(self, pod_name, cni_params):
        """
        Remove the pod from the interfaces_q and provision the interface
        (program the transit agent)
        """
        interfaces = self.interfaces.get(pod_name, [])
        for interface in interfaces:
            if interface.status == InterfaceStatus.queued:
                self._ProvisionInterface(interface, cni_params)
                interface.status = InterfaceStatus.consumed

        interfaces = InterfacesList(interfaces=interfaces)
        return interfaces

    def _ProvisionInterface(self, interface, cni_params):
        """
        Provision the interface according to its type
        """
        if interface.interface_type == InterfaceType.veth:
            self._ProvisionVethInterface(interface, cni_params)

    def _ProvisionVethInterface(self, interface, cni_params):
        """
        Provision a veth interface.
        """
        # Finalize all interface configuration. All main interface configuration
        # will be in the CNI. All the peer interface configuration, will be here
        # Network namespace operations (Move these to the CNI)

        veth_peer_index = get_iface_index(interface.veth.peer, self.iproute)
        if os.getenv('FEATUREGATE_BWQOS', 'false').lower() in ('false', '0'):
            self.iproute.link('set', index=veth_peer_index,
                              state='up', mtu=9000)
        else:
            mzbr_index = get_iface_index(CONSTANTS.MIZAR_BRIDGE, self.iproute)
            self.iproute.link('set', index=veth_peer_index,
                              master=mzbr_index, state='up', mtu=9000)

        # Configure the Transit Agent
        self._ConfigureTransitAgent(interface)

    def _ConfigureTransitAgent(self, interface):
        """
        Load the Transit Agent XDP program, program all the bouncer substrate,
        update the agent metadata and endpoint.
        """
        logger.info("Loading transit agent.")
        self.rpc.load_transit_agent_xdp(interface)

        for bouncer in interface.bouncers:
            self.rpc.update_agent_substrate_ep(
                interface.veth.peer, bouncer.ip_address, bouncer.mac)
        self.rpc.update_agent_metadata(interface)
        self.rpc.update_ep(interface)
        self.rpc.update_packet_metadata(interface.veth.peer, interface)

    def ConsumeInterfaces(self, request, context):
        """
        Called by the CNI to consume queued interfaces for a specific POD
        """
        cni_params = request
        requested_pod_id = cni_params.pod_id
        requested_pod_name = get_pod_name(requested_pod_id)
        logger.info(
            "Call from CNI Consume: cni_params/request: {}, cni_params.pod_id {}, pod_name {}".format(request, request.pod_id, requested_pod_name))
        logger.info("Consume Interfaces {}".format(request))
        logger.info("Consuming interfaces for pod: {} Current Queue: {}".format(
            requested_pod_name, list(self.pod_dict)))

        # The success of this function depends on ProduceInterfaces which is executed in another process.
        # So using while here to wait until ProduceInterfaces has been done.
        start = time.time()
        while True:
            if self.pod_dict:
                if requested_pod_name in self.pod_dict:
                    if self.pod_dict[requested_pod_name]:
                        # Interfaces for the Pod has been produced
                        return self._ConsumeInterfaces(requested_pod_name, request)
            time.sleep(WAITING_SLEEP_INTERVAL)
            now = time.time()
            if now - start >= CONSUME_INTERFACE_TIMEOUT:
                break

        # If we are here, the endpoint operator has not produced any interfaces
        # for the Pod. Typically the CNI will retry to consume the interface.
        raise RuntimeError(
            "ConsumeInterfaces: Interface not found for pod '{}'".format(requested_pod_name))

    def RemoveCachedInterfaces(self, request, context):
        """
        Called by the endpoints operator to remove cached interfaces.
        """
        requested_pod_id = request
        requested_pod_name = get_pod_name(requested_pod_id)
        if(requested_pod_name in self.pod_dict):
            self.pod_dict.pop(requested_pod_name)
        if(requested_pod_name in self.interfaces):
            self.interfaces.pop(requested_pod_name)

        return empty_pb2.Empty()

    def _DeleteVethInterface(self, interface):
        """
        Delete a veth interface
        """
        veth_peer_index = get_iface_index(interface.veth.peer, self.iproute)
        self.rpc.unload_transit_agent_xdp(interface)
        self.iproute.link('delete', index=veth_peer_index)

    def DeleteInterface(self, request, context):
        """
        Delete network interface
        """
        interface = request
        pod_name = get_pod_name(interface.interface_id.pod_id)
        pod_interfaces = self.interfaces.get(pod_name, [])
        iface = interface.interface_id.interface
        logger.info("Deleting interfaces for pod {} with interfaces {}".format(
            pod_name, pod_interfaces))

        for pod_interface in pod_interfaces:
            self.interfaces[pod_name].remove(pod_interface)
            if iface == pod_interface and pod_interface.interface_type == InterfaceType.veth:
                logger.info("Deleting interface: {}".format(iface))
                self._DeleteVethInterface(pod_interface)
                logger.info("Removed {}".format(pod_interface))

        return empty_pb2.Empty()

    def ActivateHostInterface(self, request, context):
        interface = request

        # Provision host veth interface and load transit xdp agent.
        veth_peer_index = get_iface_index(interface.veth.peer, self.iproute)
        self.iproute.link('set', index=veth_peer_index,
                          state='up', mtu=9000)
        self.rpc.load_transit_agent_xdp(interface)

        veth_index = get_iface_index(interface.veth.name, self.iproute)
        # configure and activate interfaces
        self.iproute.link('set', index=veth_index,
                          ifname=interface.veth.name)
        self.iproute.link('set', index=veth_index, state='up')

        # Setting the prefix length of the veth device to a large range adds a route to
        # the host. Since this device has the same IP address as the host's main
        # interface, this will affect the host network causing host traffic to be routed
        # to the wrong interface. Here we set the prefix length to 32.
        self.iproute.addr('add', index=veth_index, address=interface.address.ip_address,
                          prefixlen=int(interface.address.ip_prefix))

        self.iproute.route('add', dst=interface.subnet_ip,
                           mask=int(interface.subnet_prefix), oif=veth_index)
        # Disable TSO and checksum offload as xdp currently does not support
        logger.info("Disable tso for host ep")
        cmd = "nsenter -t 1 -m -u -n -i ethtool -K {} tso off gso off ufo off".format(
            interface.veth.name)
        rc, text = run_cmd(cmd)
        logger.info("Disabled tso rc:{} text{}".format(rc, text))
        logger.info("Disable rx tx offload for host ep")
        cmd = "nsenter -t 1 -m -u -n -i ethtool --offload {} rx off tx off".format(
            interface.veth.name)
        rc, text = run_cmd(cmd)
        logger.info(
            "Disabled rx tx offload for host ep rc: {} text: {}".format(rc, text))

        cmd = "nsenter -t 1 -m -u -n -i cat /sys/class/net/{}/speed".format(
            interface.veth.name)
        rc, linkspeed = run_cmd(cmd)
        linkspeed_bytes_per_sec = int(
            int(linkspeed.rstrip('\r\n')) * 1000 * (1000 / 8))
        logger.info("Host interface {} Link Speed {} bytes/sec".format(
            interface.veth.name, linkspeed_bytes_per_sec))

        # Initialize Tx stats map entry
        # TODO: Use interface.address.ip_address for multi-NIC scenario
        self.rpc.reset_tx_stats("0.0.0.0")

        # TODO: Get user-configured default bandwidth limit percentage from config-map
        bwlimit = int((linkspeed_bytes_per_sec *
                      CONSTANTS.MIZAR_DEFAULT_EGRESS_BW_LIMIT_PCT) / 100)
        self.rpc.update_bw_qos_config(interface.address.ip_address, bwlimit)

        return interface


class InterfaceServiceClient():
    def __init__(self, ip):
        addr = '{}:{}'.format(ip, OBJ_DEFAULTS.mizar_daemon_service_port)
        self.channel = grpc.insecure_channel(addr)
        self.stub = InterfaceServiceStub(self.channel)

    def InitializeInterfaces(self, interfaces_list, task):
        try:
            resp = self.stub.InitializeInterfaces(interfaces_list)
            return resp
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                task.raise_temporary_error(
                    "InitializeInterfaces failed, Daemon not ready {}".format(rpc_error.details()))
            else:
                task.raise_permanent_error(
                    "Unknown gRPC error {}".format(rpc_error.details()))

    def ProduceInterfaces(self, interfaces_list, task):
        try:
            resp = self.stub.ProduceInterfaces(interfaces_list)
            return resp
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                task.raise_temporary_error(
                    "Produce endpoint temporary error: Daemon not yet ready! {}".format(rpc_error.details()))
            elif CONSTANTS.GRPC_DEVICE_BUSY_ERROR in rpc_error.details() or CONSTANTS.GRPC_FILE_EXISTS_ERROR in rpc_error.details():
                logger.info(
                    "Produce endpoint permanent error: Repeat call veth device already created! RPC error : {}".format(rpc_error.details()))
                return None
            else:
                task.raise_permanent_error(
                    "Produce endpoint permanent error: Unknown {}".format(rpc_error.details()))

    # Unused by operator
    def ConsumeInterfaces(self, pod_id):
        resp = self.stub.ConsumeInterfaces(pod_id)
        return resp

    def DeleteInterface(self, interface, task):
        try:
            resp = self.stub.DeleteInterface(interface)
            return resp
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                task.raise_temporary_error(
                    "DeleteInterface failed, Daemon not ready {}".format(rpc_error.details()))
            else:
                task.raise_permanent_error(
                    "Unknown gRPC error {}".format(rpc_error.details()))

    def ActivateHostInterface(self, interface, task):
        try:
            resp = self.stub.ActivateHostInterface(interface)
            return resp
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                task.raise_temporary_error(
                    "Produce host endpoint temporary error: Daemon not yet ready! {}".format(rpc_error.details()))
            elif CONSTANTS.GRPC_DEVICE_BUSY_ERROR in rpc_error.details() or CONSTANTS.GRPC_FILE_EXISTS_ERROR in rpc_error.details():
                logger.info(
                    "Produce host endpoint: Repeat call, veth device already created! RPC error: {}".format(rpc_error.details()))
                return None
            else:
                task.raise_permanent_error(
                    "Produce host endpoint permanent error: Unknown {}".format(rpc_error.details()))

    def RemoveCachedInterfaces(self, pod_id, task):
        try:
            resp = self.stub.RemoveCachedInterfaces(pod_id)
            return resp
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                task.raise_temporary_error(
                    "Remove cached interfaces temporary error: Daemon not yet ready! {}".format(rpc_error.details()))
            else:
                task.raise_permanent_error(
                    "Remove cached interfaces temporary error: Unknown {}".format(rpc_error.details()))

class LocalTransitRpc:
    def __init__(self, ip, mac, itf, benchmark=False):
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
        self.trn_cli_update_packet_metadata = f'''{self.trn_cli} update-packet-metadata'''
        self.trn_cli_delete_packet_metadata = f'''{self.trn_cli} delete-packet-metadata'''
        self.trn_cli_update_tx_stats = f'''{self.trn_cli} update-tx-stats -i {self.phy_itf} -j'''
        self.trn_cli_update_bw_qos_config = f'''{self.trn_cli} update-bw-qos-config -i {self.phy_itf} -j'''
        self.trn_cli_delete_bw_qos_config = f'''{self.trn_cli} delete-bw-qos-config -i {self.phy_itf} -j'''
        self.trn_cli_get_bw_qos_config = f'''{self.trn_cli} get-bw-qos-config -i {self.phy_itf} -j'''

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
            "pcapfile": agent_pcap_file,
            "xdp_flag": CONSTANTS.XDP_GENERIC
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_load_transit_agent_xdp} -i \'{itf}\' -j \'{jsonconf}\' '''
        logger.info("load_transit_agent_xdp: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info(
            "load_transit_agent_xdp returns {} {}".format(returncode, text))

    def unload_transit_agent_xdp(self, interface):
        itf = interface.veth.peer
        jsonconf = '\'{}\''
        cmd = f'''{self.trn_cli_unload_transit_agent_xdp} -i \'{itf}\' -j {jsonconf} '''
        logger.info("unload_transit_agent_xdp: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info(
            "unload_transit_agent_xdp returns {} {}".format(returncode, text))

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

    def update_packet_metadata(self, veth_peer, interface):
        itf = veth_peer
        jsonconf = {
            "tunnel_id": interface.address.tunnel_id,
            "ip": interface.address.ip_address,
            "pod_label_value": interface.pod_label_value,
            "namespace_label_value": interface.namespace_label_value,
            "egress_bandwidth_bytes_per_sec": interface.egress_bandwidth_bytes_per_sec,
            "pod_network_class": interface.pod_network_class,
            "pod_network_priority": interface.pod_network_priority
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_update_packet_metadata} -i \'{itf}\' -j \'{jsonconf}\''''
        logger.info("update_packet_metadata: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info(
            "update_packet_metadata returns {} {}".format(returncode, text))

    def update_agent_metadata(self, interface):
        itf = interface.veth.peer
        default_itf = get_itf()
        netip = str(ipaddress.ip_interface(
            interface.address.ip_address + '/' + interface.address.ip_prefix).network.network_address)
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
                "hosted_iface": default_itf
            },
            "net": {
                "tunnel_id": interface.address.tunnel_id,
                "nip":  netip,
                "prefixlen":  interface.address.ip_prefix,
                "switches_ips": bouncers
            },
            "eth": {
                "ip": interface.droplet.ip_address,
                "mac": interface.droplet.mac,
                "iface": default_itf
            }
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_update_agent_metadata} -i \'{itf}\' -j \'{jsonconf}\''''
        logger.info("update_agent_metadata: {}".format(cmd))
        returncode, text = run_cmd(cmd)
        logger.info(
            "update_agent_metadata returns {} {}".format(returncode, text))

    def reset_tx_stats(self, ipaddr):
        jsonconf = {
            "src_addr": ipaddr,
            "tx_pkts_xdp_redirect": 0,
            "tx_bytes_xdp_redirect": 0,
            "tx_pkts_xdp_pass": 0,
            "tx_bytes_xdp_pass": 0,
            "tx_pkts_xdp_drop": 0,
            "tx_bytes_xdp_drop": 0
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_update_tx_stats} \'{jsonconf}\''''
        returncode, text = run_cmd(cmd)
        logger.info(
            "update_tx_stats returns {} {}".format(returncode, text))

    def update_bw_qos_config(self, ipaddr, egress_bw_bps):
        jsonconf = {
            "src_addr": ipaddr,
            "egress_bandwidth_bytes_per_sec": egress_bw_bps
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_update_bw_qos_config} \'{jsonconf}\''''
        returncode, text = run_cmd(cmd)
        logger.info(
            "update_bw_qos_config returns {} {}".format(returncode, text))

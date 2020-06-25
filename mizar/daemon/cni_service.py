import logging
import sys
import os
import subprocess
import mizar.proto.cni_pb2 as cni_pb2
import mizar.proto.cni_pb2_grpc as cni_pb2_grpc
import time
import grpc
import json
import fs
from mizar.common.common import *
from concurrent import futures
from google.protobuf import empty_pb2
from mizar.common.rpc import TrnRpc
import queue

logger = logging.getLogger()


class CniServer(cni_pb2_grpc.CniServiceServicer):

    def __init__(self):
        self.pod_add_q = queue.Queue()
        self.iproute = IPRoute()
        self.interfaces = {}

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

        self.mem_fs = fs.open_fs('mem://')
        self.mem_fs.makedirs('mizar')

    @property
    def rpc(self):
        return TrnRpc('127.0.0.1', self.droplet_mac)

    def AddPod(self, request, context):
        pod = request

        # Add the pod object to the pod_add_q for cni add to unblock
        self.pod_add_q.put(pod)
        logger.info("Add Pod called {}".format(pod))
        return empty_pb2.Empty()

    def _provision_simple_endpoint(self, pod):
        logger.info("Provision simple endpoint {}, {}".format(cni_params, pod))
        pass

    def DelPod(self, request, context):
        pass

    def Cni(self, request, context):
        cni_params = request
        switcher = {
            'ADD': self._add,
            'DEL': self._delete,
            'GET': self._get,
            'VERSION': self._version
        }
        return switcher.get(cni_params.command, self._cni_error)(cni_params)

    def _cni_error(self, cni_params):
        return cni_pb2.CniResults(result="Unsuported cni command", value=1)

    def provision_endpoint(self, ep, iproute_ns):
        # ip netns exec {ep.ns} sysctl -w net.ipv4.tcp_mtu_probing=2 && \
        # ip netns exec {ep.ns} ethtool -K veth0 tso off gso off ufo off && \
        # ip netns exec {ep.ns} ethtool --offload veth0 rx off tx off && \

        logging.debug("Add address to ep {}".format(ep.name))
        iproute_ns.addr('add', index=ep.veth_index,
                        address=ep.ip, prefixlen=int(ep.prefix))

        logging.debug("Add route to default GW to ep {}".format(ep.name))
        iproute_ns.route('add', gateway=ep.gw)

    def create_mizarnetns(self, cni_netns, mizar_netns):
        os.makedirs('/var/run/netns/', exist_ok=True)
        f = os.listdir('/var/run/netns/')
        logging.debug("files ns {}".format(f))
        src = cni_netns
        dst = '/var/run/netns/{}'.format(mizar_netns)
        os.symlink(src, dst)
        logging.debug("Created namespace {} from {}".format(
            mizar_netns, cni_netns))
        return NetNS(mizar_netns)

    def allocate_local_id(self, container_id):
        e = [1]
        v = [1]
        while len(e) or len(v):
            localid = container_id[-8:]
            eth = "eth-" + localid
            veth = 'veth-' + localid
            e = self.iproute.link_lookup(ifname=eth)
            v = self.iproute.link_lookup(ifname=veth)

        return localid

    def _add(self, cni_params):
        logger.info(
            "cni add called, and wait for POD RPC {}".format(cni_params))

        pod_name = get_pod_name(cni_params.pod_id)
        result_file_path = '/mizar/{}'.format(pod_name)

        # 1.  Create Mizar netns
        local_id = self.allocate_local_id(cni_params.container_id)
        mizar_netns = "mizar-" + local_id
        iproute_ns = self.create_mizarnetns(cni_params.netns, mizar_netns)

        # 2. Prepare veth pair of the simple endpoint
        veth_name = "eth-" + local_id
        veth_peer = "veth-" + local_id

        self.iproute.link('add', ifname=veth_name, peer=veth_peer, kind='veth')

        veth_index = get_iface_index(veth_name, self.iproute)
        veth_peer_index = get_iface_index(veth_peer, self.iproute)

        veth_mac = get_iface_mac(veth_index, self.iproute)
        veth_peer_mac = get_iface_mac(veth_peer_index, self.iproute)

        self.iproute.link('set', index=veth_index, net_ns_fd=mizar_netns)
        iproute_ns.link('set', index=veth_index, ifname=cni_params.interface)

        lo_idx = self.iproute.link_lookup(ifname="lo")[0]
        iproute_ns.link('set', index=lo_idx, state='up')

        iproute_ns.link('set', index=veth_index, state='up')
        self.iproute.link('set', index=veth_peer_index, state='up', mtu=9000)

        self.rpc.load_transit_agent_xdp(veth_peer)

        pod_itfs = self.interfaces.get(
            pod_name, cni_pb2.PodInterfaces(pod_id=cni_params.pod_id))

        pod_name.interfaces[cni_params.interface]
        # Put the results in /tmp/container_id

        # # Wait for IP addresses
        # while True:
        #     # TODO: manage expiry and recycle pod objects
        #     # block until a pod item is in the queue
        #     pod = self.pod_add_q.get()
        #     if pod.name == cni_params.k8s_pod_name:
        #         break
        #     # put it back and wait again
        #     self.pod_add_q.put(pod)

        # Now we have all the information we need

        # result = cni_pb2.CniResults(result=json.dumps(
        #     {
        #         "cniVersion": cni_params.cni_version,
        #         "interfaces": [
        #             {
        #                 "name": pod.veth_name,
        #                 "mac": pod.mac,
        #                 "sandbox": pod.netns
        #             }
        #         ],
        #         "ips": [
        #             {
        #                 "version": "4",
        #                 "address": "{}/{}".format(pod.ip, pod.prefix),
        #                 "gateway": pod.gw,
        #                 "interface": 0
        #             }
        #         ]
        #     }
        # ),
        #     value=0)

        result = cni_pb2.CniResults(result_string='', result_file_path=result_file_path,
                                    value=cni_pb2.CniResultsValue.file_pending)
        return result

    def _delete(self, cni_params):
        logger.info("cni delete called")
        result = cni_pb2.CniResults(
            result_string="", value=cni_pb2.CniResultsValue.string_failed)
        return result

    def _get(self, cni_params):
        logger.info("cni get called")
        result = cni_pb2.CniResults(
            result_string="", value=cni_pb2.CniResultsValue.string_failed)
        return result

    def _version(self, cni_params):
        logger.info("cni version called")
        result = cni_pb2.CniResults(result_string=json.dumps(
            {
                'cniVersion': '0.3.1',
                "supportedVersions": ["0.2.0", "0.3.0", "0.3.1"]
            }
        ),
            value=CniResultsValue.string_success)
        return result


class CniClient():
    def __init__(self, ip):
        self.channel = grpc.insecure_channel('{}:50051'.format(ip))
        self.stub = cni_pb2_grpc.CniServiceStub(self.channel)

    def Cni(self, params):
        resp = self.stub.Cni(params)
        return resp

    def AddPod(self, pod):
        resp = self.stub.AddPod(pod)
        return resp

    def DelPod(self, podid):
        resp = self.stub.DelPod(podid)
        return resp

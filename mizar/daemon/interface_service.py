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

    @property
    def rpc(self):
        return TrnRpc('127.0.0.1', self.droplet_mac)

    def ProduceInterfaces(self, request, context):
        interfaces = request
        requested_pod_name = get_pod_name(interfaces.pod_id)
        logger.debug("Producing interfaces for pod {}".format(
            requested_pod_name))
        for interface in interfaces.interfaces:
            self._QueueInterface(interface)
        return interfaces

    def _QueueInterface(self, interface):
        pod_name = get_pod_name(interface.interface_id.pod_id)

        with self.interfaces_lock:
            if pod_name not in self.interfaces:
                self.interfaces[pod_name] = []
            self.interfaces[pod_name].append(interface)

            if pod_name not in self.queued_pods:
                self.interfaces_q.put(pod_name)
                self.queued_pods.add(pod_name)

        interface.status = InterfaceStatus.queued

    def _ConsumeInterfaces(self, pod_name):
        with self.interfaces_lock:
            self.queued_pods.remove(pod_name)
            interfaces = self.interfaces.get(pod_name, [])
            for interface in interfaces:
                if interface.status == InterfaceStatus.queued:
                    interface.status = InterfaceStatus.consumed

        return InterfacesList(interfaces=interfaces)

    def ConsumeInterfaces(self, request, context):

        requested_pod_id = request
        requested_pod_name = get_pod_name(requested_pod_id)
        logger.debug(
            "Consuming interfaces for pod {}".format(requested_pod_name))
        start = time.time()

        # The following is a synchronization mechanism to make sure the
        # CNI calls _ConsumeInterfaces after the interfaces got produced.
        # In Arktos, this may be skipped because the Kubelet will only
        # invoike CNI after the Pod operator marks the pod's network ready

        while True:
            try:
                queued_pod_name = self.interfaces_q.get(
                    timeout=CONSUME_INTERFACE_TIMEOUT)
            except:
                break

            if queued_pod_name == requested_pod_name:
                return self._ConsumeInterfaces(queued_pod_name)

            self.interfaces_q.put(queued_pod_name)
            now = time.time()

            if now - start >= CONSUME_INTERFACE_TIMEOUT:
                break

        return self._ConsumeInterfaces(requested_pod_name)

    def DeleteInterface(self, request, context):
        # NOOP for now
        return empty_pb2.Empty()


class InterfaceServiceClient():
    def __init__(self, ip):
        self.channel = grpc.insecure_channel('{}:50051'.format(ip))
        self.stub = InterfaceServiceStub(self.channel)

    def ProduceInterfaces(self, interfaces_list):
        resp = self.stub.ProduceInterfaces(interfaces_list)
        return resp

    def ConsumeInterfaces(self, pod_id):
        resp = self.stub.ConsumeInterfaces(pod_id)
        return resp

    def DeleteInterface(self, interface_id):
        resp = self.stub.DeleteInterface(interface_id)
        return resp

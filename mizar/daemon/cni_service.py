import logging
import sys
import os
import subprocess
import mizar.proto.cni_pb2 as cni_pb2
import mizar.proto.cni_pb2_grpc as cni_pb2_grpc
import time
import grpc
import json
from concurrent import futures
from google.protobuf import empty_pb2
import queue

logger = logging.getLogger()


class CniServer(cni_pb2_grpc.CniServiceServicer):

    def __init__(self):
        self.pod_add_q = queue.Queue()

    def AddPod(self, request, context):
        pod = request
        self.pod_add_q.put(pod)
        logger.info("Add Pod called {}".format(pod))
        return empty_pb2.Empty()

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

    def _add(self, cni_params):
        logger.info(
            "cni add called, and wait for POD RPC {}".format(cni_params))
        while True:
            # block until an item is in the queue
            pod = self.pod_add_q.get()
            if pod.name == cni_params.k8s_pod_name:
                break
            # put it back and wait again
            self.pod_add_q.put(pod)

        # TODO: add veth peer, etc

        logger.info("POD Ready {}".format(pod))

        result = cni_pb2.CniResults(result=json.dumps(
            {
                "cniVersion": cni_params.cni_version,
                "interfaces": [
                    {
                        "name": pod.veth_name,
                        "mac": pod.mac,
                        "sandbox": pod.netns
                    }
                ],
                "ips": [
                    {
                        "version": "4",
                        "address": "{}/{}".format(pod.ip, pod.prefix),
                        "gateway": pod.gw,
                        "interface": 0
                    }
                ]
            }
        ),
            value=0)
        return result

    def _delete(self, cni_params):
        logger.info("cni delete called")
        result = cni_pb2.CniResults(result="", value=1)
        return result

    def _get(self, cni_params):
        logger.info("cni get called")
        result = cni_pb2.CniResults(result="", value=1)
        return result

    def _version(self, cni_params):
        logger.info("cni version called")
        result = cni_pb2.CniResults(result=json.dumps(
            {
                'cniVersion': '0.3.1',
                "supportedVersions": ["0.2.0", "0.3.0", "0.3.1"]
            }
        ),
            value=0)
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

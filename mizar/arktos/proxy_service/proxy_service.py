import logging
import sys
import os
import subprocess
import time
import grpc
from kubernetes import client, config
from concurrent import futures
from google.protobuf import empty_pb2
from mizar.obj.vpc import Vpc
from mizar.obj.net import Net
from mizar.obj.divider import Divider
from mizar.common.cidr import Cidr
from mizar.store.operator_store import OprStore
from mizar.proto.arktos_pb2_grpc import ArktosNetworkServiceServicer,  ArktosNetworkServiceStub
from mizar.proto.builtins_pb2_grpc import BuiltinsServiceServicer, BuiltinsServiceStub
logger = logging.getLogger()


class ProxyServer(ArktosNetworkServiceServicer, BuiltinsServiceServicer):

    def __init__(self):
        self.store = OprStore()
        config.load_incluster_config()
        self.obj_api = client.CustomObjectsApi()

    def CreatePod(self, request, context):
        pass

    def CreateService(self, request, context):
        pass

    def CreateNode(self, request, context):
        pass

    def UpdatePod(self, request, context):
        pass

    def UpdateService(self, request, context):
        pass

    def UpdateNode(self, request, context):
        pass

    def ResumePod(self, request, context):
        pass

    def ResumeService(self, request, context):
        pass

    def ResumeNode(self, request, context):
        pass


class ProxyServiceClient():
    def __init__(self, ip):
        self.channel = grpc.insecure_channel('{}:50051'.format(ip))
        self.stub_arktos = ArktosNetworkServiceStub(self.channel)
        self.stub_builtins = BuiltinsServiceStub(self.channel)

    def CreatePod(self, BuiltinsMessage):
        resp = self.stub_builtins.CreatePod(BuiltinsMessage)
        return resp

    def CreateService(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateService(BuiltinsMessage)
        return resp

    def CreateNode(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateNode(BuiltinsMessage)
        return resp

    def UpdatePod(self, BuiltinsMessage):
        resp = self.stub_builtins.CreatePod(BuiltinsMessage)
        return resp

    def UpdateService(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateService(BuiltinsMessage)
        return resp

    def UpdateNode(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateNode(BuiltinsMessage)
        return resp

    def ResumePod(self, BuiltinsMessage):
        resp = self.stub_builtins.CreatePod(BuiltinsMessage)
        return resp

    def ResumeService(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateService(BuiltinsMessage)
        return resp

    def ResumeNode(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateNode(BuiltinsMessage)
        return resp

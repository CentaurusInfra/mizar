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
from mizar.proto.vpcs_pb2_grpc import VpcsServiceServicer, VpcsServiceStub
from mizar.proto.nets_pb2_grpc import NetsServiceServicer, NetsServiceStub
from mizar.proto.builtins_pb2_grpc import BuiltinsServiceServicer, BuiltinsServiceStub
logger = logging.getLogger()


class ProxyServer(VpcsServiceServicer, NetsServiceServicer):

    def __init__(self):
        self.store = OprStore()
        config.load_incluster_config()
        self.obj_api = client.CustomObjectsApi()

    # CRD API calls
    def CreateVpc(self, request, context):
        vpc = Vpc(request.Name, self.obj_api, self.store)
        logger.info("Creating VPC from PROXY SERVER")
        vpc.cidr = Cidr(request.Prefix,
                        request.Ip)
        vpc.vni = request.Vni
        vpc.n_dividers = request.Dividers
        vpc.create_obj()
        return empty_pb2.Empty()

    def CreateNet(self, request, context):
        net = Net(request.Name, self.obj_api, self.store)
        logger.info("Creating Net {} from PROXY SERVER".format(request.Name))
        net.vpc = request.Vpc
        net.vni = request.Vni
        net.cidr = Cidr(request.Prefix,
                        request.Ip)
        net.n_bouncers = request.bouncers
        net.create_obj()
        return empty_pb2.Empty()

    # Builtins. Will Call Workflows instead of using CRD API
    def CreatePod(self, request, context):
        pass

    def CreateService(self, request, context):
        pass

    def CreateNode(self, request, context):
        pass


class ProxyServiceClient():
    def __init__(self, ip):
        self.channel = grpc.insecure_channel('{}:50051'.format(ip))
        self.stub_vpc = VpcsServiceStub(self.channel)
        self.stub_net = NetsServiceStub(self.channel)
        self.stub_builtins = BuiltinsServiceStub(self.channel)

    def CreateVpc(self, VpcMessage):
        resp = self.stub_vpc.CreateVpc(VpcMessage)
        return resp

    def CreateNet(self, NetMessage):
        resp = self.stub_net.CreateNet(NetMessage)
        return resp

    def CreatePod(self, BuiltinsMessage):
        resp = self.stub_builtins.CreatePod(BuiltinsMessage)
        return resp

    def CreateService(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateService(BuiltinsMessage)
        return resp

    def CreateNode(self, BuiltinsMessage):
        resp = self.stub_builtins.CreateNode(BuiltinsMessage)
        return resp

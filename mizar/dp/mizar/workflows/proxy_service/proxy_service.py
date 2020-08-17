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
from mizar.store.operator_store import OprStore
from mizar.proto.vpcs_pb2_grpc import VpcsServiceServicer, VpcsServiceStub
from mizar.proto.nets_pb2_grpc import NetsServiceServicer, NetsServiceStub
logger = logging.getLogger()


class ProxyServer(VpcsServiceServicer, NetsServiceServicer):

    def __init__(self):
        self.store = OprStore()
        config.load_incluster_config()
        self.obj_api = client.CustomObjectsApi()

    def CreateVpc(self, request, context):
        vpc = Vpc(request.Name, self.obj_api, self.store)
        logger.info("Creating VPC from PROXY SERVER")
        vpc.create_obj()
        return empty_pb2.Empty()

    def CreateNet(self, request, context):
        net = Net(request.Name, self.obj_api, self.store)
        logger.info("Creating Net from PROXY SERVER")
        net.create_obj()
        return empty_pb2.Empty()


class ProxyServiceClient():
    def __init__(self, ip):
        self.channel = grpc.insecure_channel('{}:50051'.format(ip))
        self.stub_vpc = VpcsServiceStub(self.channel)
        self.stub_net = NetsServiceStub(self.channel)

    def CreateVpc(self, VpcMessage):
        resp = self.stub_vpc.CreateVpc(VpcMessage)
        return resp

    def UpdateVpc(self, VpcMessage):
        resp = self.stub_vpc.UpdateVpc(VpcMessage)
        return resp

    def ReadVpc(self, VpcId):
        resp = self.stub_vpc.ReadVpc(VpcId)
        return resp

    def DeleteVpc(self, VpcId):
        resp = self.stub_vpc.DeleteVpc(VpcId)
        return resp

    def ResumeVpc(self, VpcId):
        resp = self.stub_vpc.ResumeVpc(VpcId)
        return resp

    def CreateNet(self, NetMessage):
        resp = self.stub_net.CreateNet(NetMessage)
        return resp

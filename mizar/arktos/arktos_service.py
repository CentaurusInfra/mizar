# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Phu Tran          <@phudtran>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
from mizar.obj.endpoint import Endpoint
from mizar.common.cidr import Cidr
from mizar.store.operator_store import OprStore
from mizar.proto.arktos_pb2_grpc import ArktosNetworkServiceServicer,  ArktosNetworkServiceStub
from mizar.proto.builtins_pb2_grpc import BuiltinsServiceServicer, BuiltinsServiceStub
from mizar.common.workflow import *
from mizar.dp.mizar.operators.droplets.droplets_operator import *
from mizar.dp.mizar.operators.bouncers.bouncers_operator import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.vpcs.vpcs_operator import *
from mizar.proto.builtins_pb2 import *
from mizar.common.wf_param import *
from mizar.common.wf_factory import wffactory

vpc_opr = VpcOperator()
logger = logging.getLogger()


class ArktosService(BuiltinsServiceServicer):

    def __init__(self):
        self.store = OprStore()
        config.load_incluster_config()
        self.obj_api = client.CustomObjectsApi()

    def CreatePod(self, request, context):
        logger.info("Creating pod from Arktos Service {}".format(request.name))
        param = HandlerParam()
        param.name = request.name
        param.body['status'] = {}
        param.body['metadata'] = {}
        param.body['metadata']["annotations"] = {}
        param.body['metadata']["labels"] = {}

        param.body['status']['hostIP'] = request.host_ip
        param.body['metadata']['name'] = request.name
        param.body['metadata']['namespace'] = request.namespace
        param.body['status']['phase'] = request.phase

        param.body['metadata']["labels"] = OBJ_DEFAULTS.arktos_pod_label
        if request.vpc != "":
            param.body['metadata']["labels"][OBJ_DEFAULTS.arktos_pod_annotation] = request.vpc

        if len(request.interfaces) > 0:
            param.body['metadata']["annotations"][OBJ_DEFAULTS.arktos_pod_annotation] = list()
            itf_string = '['
            for interface in request.interfaces:
                itf_string += '{"name": "{}", "ip": "{}", "subnet": "{}"},'.format(
                    interface.name, interface.ip, interface.subnet)
            itf_string = itf_string[:-1] + ']'
            param.body['metadata']["annotations"][OBJ_DEFAULTS.arktos_pod_annotation] = itf_string
        return run_arktos_workflow(wffactory().k8sPodCreate(param=param))

    def CreateNode(self, request, context):
        logger.info(
            "Creating droplet from Arktos Service {}".format(request.ip))
        param = HandlerParam()
        param.body['status'] = {}
        param.body['status']['addresses'] = list()
        param.body['status']['addresses'].append({})

        param.body['status']['addresses'][0]["type"] = "InternalIP"
        param.body['status']['addresses'][0]["address"] = request.ip
        return run_arktos_workflow(wffactory().k8sDropletCreate(param=param))

    def CreateService(self, request, context):
        logger.info(
            "Create scaled endpoint from Network Controller {}.".format(request.name))
        param = HandlerParam()
        param.name = request.name
        param.body['metadata'] = {}

        param.body['metadata']['namespace'] = request.namespace
        param.spec["clusterIP"] = request.ip
        return run_arktos_workflow(wffactory().k8sServiceCreate(param=param))

    def CreateServiceEndpoint(self, request, context):
        logger.info("Create Service Endpoint from Network Controller")
        param = HandlerParam()
        param.name = request.name
        param.body['metadata'] = {}
        param.body["metadata"]["namespace"] = request.namespace
        param.extra = request
        return run_arktos_workflow(wffactory().k8sEndpointsUpdate(param=param))

    def CreateArktosNetwork(self, request, context):
        rc = ReturnCode(
            code=CodeType.OK,
            message="OK"
        )
        if vpc_opr.store_get(request.vpc):
            rc.code = CodeType.PERM_ERROR
            rc.message = "ERROR: VPC Does not exist."
        return rc

    def UpdateArktosNetwork(self, request, context):
        self.CreateArktosNetwork(request, context)

    def ResumeArktosNetowrk(self, request, context):
        self.CreateArktosNetwork(request, context)

    def ResumePod(self, request, context):
        self.CreatePod(request, context)

    def ResumeNode(self, request, context):
        self.CreateNode(request, context)

    def ResumeService(self, request, context):
        self.CreateService(request, context)

    def ResumeServiceEndpoint(self, request, context):
        self.CreateServiceEndpoint(request, context)

    def UpdatePod(self, request, context):
        self.CreatePod(request, context)

    def UpdateNode(self, request, context):
        self.CreateNode(request, context)

    def UpdateService(self, request, context):
        self.CreateService(request, context)

    def UpdateServiceEndpoint(self, request, context):
        self.CreateServiceEndpoint(request, context)


class ArktosServiceClient():
    def __init__(self, ip):
        self.channel = grpc.insecure_channel('{}:50052'.format(ip))
        self.stub_builtins = BuiltinsServiceStub(self.channel)

    def CreatePod(self, BuiltinsPodMessage):
        resp = self.stub_builtins.CreatePod(BuiltinsPodMessage)
        return resp

    def CreateService(self, BuiltinsServiceMessage):
        resp = self.stub_builtins.CreateService(BuiltinsServiceMessage)
        return resp

    def CreateNode(self, BuiltinsNodeMessage):
        resp = self.stub_builtins.CreateNode(BuiltinsNodeMessage)
        return resp

    def UpdatePod(self, BuiltinsPodMessage):
        resp = self.stub_builtins.CreatePod(BuiltinsPodMessage)
        return resp

    def UpdateService(self, BuiltinsServiceMessage):
        resp = self.stub_builtins.CreateService(BuiltinsServiceMessage)
        return resp

    def UpdateNode(self, BuiltinsNodeMessage):
        resp = self.stub_builtins.CreateNode(BuiltinsNodeMessage)
        return resp

    def ResumePod(self, BuiltinsPodMessage):
        resp = self.stub_builtins.CreatePod(BuiltinsPodMessage)
        return resp

    def ResumeService(self, BuiltinsServiceMessage):
        resp = self.stub_builtins.CreateService(BuiltinsServiceMessage)
        return resp

    def ResumeNode(self, BuiltinsNodeMessage):
        resp = self.stub_builtins.CreateNode(BuiltinsNodeMessage)
        return resp

    def CreateArktosNetwork(self, BuiltinsArktosMessage):
        resp = self.stub_builtins.CreateArktosNetwork(BuiltinsArktosMessage)
        return resp

    def UpdateArktosNetwork(self, BuiltinsArktosMessage):
        resp = self.stub_builtins.UpdateArktosNetwork(BuiltinsArktosMessage)
        return resp

    def ResumeArktosNetowrk(self, BuiltinsArktosMessage):
        resp = self.stub_builtins.ResumeArktosNetowrk(BuiltinsArktosMessage)
        return resp

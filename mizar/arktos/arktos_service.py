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
import grpc
import json
from mizar.proto.builtins_pb2_grpc import BuiltinsServiceServicer, BuiltinsServiceStub
from mizar.common.constants import OBJ_DEFAULTS
from mizar.common.workflow import *
from mizar.dp.mizar.operators.vpcs.vpcs_operator import *
from mizar.proto.builtins_pb2 import *
from mizar.common.wf_param import *
from mizar.common.wf_factory import wffactory
from mizar.store.operator_store import OprStore

vpc_opr = VpcOperator()
logger = logging.getLogger()
store = OprStore()


class ArktosService(BuiltinsServiceServicer):

    def CreatePod(self, request, context):
        if request.host_ip == '':
            return ReturnCode(
                code=CodeType.TEMP_ERROR,
                message="Missing hostIP during pod create or update"
            )
        logger.info("Creating pod from Arktos Service {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.namespace = request.namespace
        param.body['status'] = {}
        param.body['metadata'] = {}
        param.body['metadata']['annotations'] = {}
        param.body['status']['hostIP'] = request.host_ip
        param.body['metadata']['namespace'] = request.namespace
        param.body['status']['phase'] = request.phase
        param.body['metadata']['tenant'] = request.tenant
        if not request.vpc:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Missing VPC annotation"
            )
        if not request.subnet:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Missing Subnet annotation"
            )
        param.body['metadata']['annotations'][OBJ_DEFAULTS.mizar_ep_vpc_annotation] = request.vpc
        param.body['metadata']['annotations'][OBJ_DEFAULTS.mizar_ep_subnet_annotation] = request.subnet

        param.extra = {}
        store.update_pod_namespace_store(param.name, param.namespace)
        try:
            labels = json.loads(request.labels)
        except ValueError as e:
            logger.info(
                "Client sent invalid JSON for pod labels: {} {}".format(request.labels, e))
            labels = None
        if labels:
            param.body['metadata']['labels'] = labels
            logger.info("Labels for pod {} from Arktos Service are {}".format(
                request.name, labels))
            diff_item = []
            diff_item.append('add')
            diff_item.append(tuple())
            # old
            old_dict = {}
            old_dict['metadata'] = {}
            old_dict['metadata']['labels'] = store.get_old_pod_labels(
                request.name)
            diff_item.append(old_dict)
            # new
            new_dict = {}
            new_dict['metadata'] = {}
            new_dict['metadata']['labels'] = labels
            diff_item.append(new_dict)
            diff_items = []
            diff_items.append(tuple(diff_item))
            param.diff = tuple(diff_items)
            logger.info("Pod create param.diff =  {}".format(param.diff))
            store.update_pod_label_store(
                param.name, param.body['metadata']['labels'])
        else:
            param.body['metadata']['labels'] = {}
            param.diff = tuple(tuple())
        if len(request.interfaces) > 0:
            param.extra["interfaces"] = list()
            itf_string = '['
            for interface in request.interfaces:
                itf_string += '{"name": "{}", "ip": "{}", "subnet": "{}"},'.format(
                    interface.name, interface.ip, interface.subnet)
            itf_string = itf_string[:-1] + ']'
            param.extra.interfaces = itf_string
        return run_arktos_workflow(wffactory().k8sPodCreate(param=param))

    def CreateNode(self, request, context):
        logger.info(
            "Creating droplet from Arktos Service {}".format(request.ip))
        param = reset_param(HandlerParam())
        param.body['status'] = {}
        param.body['status']['addresses'] = list()
        param.body['status']['addresses'].append({})

        param.body['status']['addresses'][0]["type"] = "InternalIP"
        param.body['status']['addresses'][0]["address"] = request.ip
        return run_arktos_workflow(wffactory().k8sDropletCreate(param=param))

    def CreateNamespace(self, request, context):
        logger.info(
            "Creating namespace from Arktos Service {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.body['status'] = {}
        param.body['metadata'] = {}
        param.body['metadata']['tenant'] = request.tenant
        if request.labels is not None and len(request.labels) != 0:
            logger.info("Labels for namespace {} from Arktos Service are {}".format(
                request.name, request.labels))
            param.body['metadata']['labels'] = json.loads(request.labels)
            diff_item = []
            diff_item.append('add')
            diff_item.append(tuple())
            # old
            old_dict = {}
            old_dict['metadata'] = {}
            old_dict['metadata']['labels'] = store.get_old_namespace_labels(
                request.name)
            diff_item.append(old_dict)
            # new
            new_dict = {}
            new_dict['metadata'] = {}
            new_dict['metadata']['labels'] = json.loads(request.labels)
            diff_item.append(new_dict)
            diff_items = []
            diff_items.append(tuple(diff_item))
            param.diff = tuple(diff_items)
            logger.info("Namespace create param.diff =  {}".format(param.diff))
            store.update_namespace_label_store(
                param.name, param.body['metadata']['labels'])
        else:
            param.body['metadata']['labels'] = {}
            param.diff = tuple(tuple())
        return run_arktos_workflow(wffactory().k8sNamespaceCreate(param=param))

    def CreateService(self, request, context):
        logger.info(
            "Create scaled endpoint from Network Controller {} {} {}.".format(request.name, request.namespace, request.tenant))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.body['metadata'] = {}
        param.body['metadata']['annotations'] = {}
        param.extra = {}
        if not request.vpc:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Missing VPC annotation"
            )
        if not request.subnet:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Missing Subnet annotation"
            )
        param.body['metadata']['annotations'][OBJ_DEFAULTS.mizar_ep_vpc_annotation] = request.vpc
        param.body['metadata']['annotations'][OBJ_DEFAULTS.mizar_ep_subnet_annotation] = request.subnet

        param.body['metadata']['namespace'] = request.namespace
        param.spec["clusterIP"] = request.ip
        logger.info("From grpc server: Service IP is {}".format(request.ip))
        param.extra["tenant"] = request.tenant
        return run_arktos_workflow(wffactory().k8sServiceCreate(param=param))

    def CreateServiceEndpointProtobuf(self, request, context):
        logger.info(
            "Create Service Endpoint from Network Controller {}".format(request.name))
        param = HandlerParam()
        param.name = request.name
        param.body['metadata'] = {}
        param.body["metadata"]["namespace"] = request.namespace
        param.extra = request
        return run_arktos_workflow(wffactory().k8sEndpointsUpdate(param=param))

    def CreateServiceEndpoint(self, request, context):
        logger.info(
            "Create Service Endpoint from Network Controller {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.body['metadata'] = {}
        param.body["metadata"]["namespace"] = request.namespace
        param.body['metadata']['tenant'] = request.tenant
        logger.info("Service Endpoint name {} namespace {} tenant {}".format(
            request.name, request.namespace, request.tenant))
        ips = json.loads(request.backend_ips_json)
        ports = json.loads(request.ports_json)
        param.extra = {}
        param.extra["request"] = request
        param.extra["backend_ips"] = ips
        param.extra["ports"] = ports
        for ip in ips:
            logger.info(ip)
        for port in ports:
            logger.info(port)
        return run_arktos_workflow(wffactory().k8sEndpointsUpdate(param=param))

    def CreateNetworkPolicy(self, request, context):
        logger.info(
            "Creating network policy from Arktos Service {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.namespace = request.namespace
        param.body['status'] = {}
        param.body['metadata'] = {}
        param.body['metadata']['namespace'] = request.namespace
        param.body['metadata']['tenant'] = request.tenant
        param.spec = json.loads(request.policy)
        param.extra = {}
        return run_arktos_workflow(wffactory().k8sNetworkPolicyCreate(param=param))

    def UpdateArktosNetwork(self, request, context):
        return self.CreateArktosNetwork(request, context)

    def ResumeArktosNetowrk(self, request, context):
        return self.CreateArktosNetwork(request, context)

    def ResumePod(self, request, context):
        return self.CreatePod(request, context)

    def ResumeNode(self, request, context):
        return self.CreateNode(request, context)

    def ResumeService(self, request, context):
        return self.CreateService(request, context)

    def ResumeServiceEndpoint(self, request, context):
        return self.CreateServiceEndpoint(request, context)

    def ResumeNetworkPolicy(self, request, context):
        return self.CreateNetworkPolicy(request, context)

    def ResumeNamespace(self, request, context):
        return self.CreateNamespace(request, context)

    def UpdatePod(self, request, context):
        if not request.vpc:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Pod Update missing VPC annotation."
            )
        if not request.subnet:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Pod update missing Subnet annotation."
            )
        return self.CreatePod(request, context)

    def UpdateNode(self, request, context):
        return self.CreateNode(request, context)

    def UpdateService(self, request, context):
        if not request.vpc:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Pod Update missing VPC annotation."
            )
        if not request.subnet:
            return ReturnCode(
                code=CodeType.PERM_ERROR,
                message="Pod update missing Subnet annotation."
            )
        return self.CreateService(request, context)

    def UpdateServiceEndpoint(self, request, context):
        return self.CreateServiceEndpoint(request, context)

    def UpdateNamespace(self, request, context):
        return self.CreateNamespace(request, context)

    def UpdateNetworkPolicy(self, request, context):
        return self.CreateNetworkPolicy(request, context)

    def DeleteNode(self, request, context):
        logger.info(
            "Deleting droplet from Network Controller {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        return run_arktos_workflow(wffactory().DropletDelete(param=param))

    def DeletePod(self, request, context):
        logger.info(
            "Deleting pod from Network Controller {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.namespace = request.namespace
        store.delete_pod_label_store(param.name)
        store.delete_pod_namespace_store(param.name)
        return run_arktos_workflow(wffactory().k8sPodDelete(param=param))

    def DeleteNamespace(self, request, context):
        logger.info(
            "Deleting namespace from Network Controller {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        store.delete_namespace_label_store(param.name)
        store.delete_namespace_pod_store(param.name)
        return run_arktos_workflow(wffactory().k8sNamespaceDelete(param=param))

    def DeleteService(self, request, context):
        logger.info(
            "Deleting servoce from Network Controller {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.body['metadata'] = {}
        param.body["metadata"]["namespace"] = request.namespace
        param.body['metadata']['tenant'] = request.tenant
        return run_arktos_workflow(wffactory().k8sServiceDelete(param=param))

    def DeleteNetworkPolicy(self, request, context):
        logger.info(
            "Deleting network policy from Network Controller {}".format(request.name))
        param = reset_param(HandlerParam())
        param.name = request.name
        param.body['metadata'] = {}
        param.body["metadata"]["namespace"] = request.namespace
        param.extra = request.tenant
        return run_arktos_workflow(wffactory().k8sNetworkPolicyDelete(param=param))

    def CreateArktosNetwork(self, request, context):
        logger.info(
            "CreateArktosNetwork to be deprecated.")
        rc = ReturnCode(
            code=CodeType.OK,
            message="OK"
        )
        return rc


class ArktosServiceClient():
    def __init__(self, ip):
        addr = '{}:{}'.format(
            ip, OBJ_DEFAULTS.mizar_operator_arktos_service_port)
        self.channel = grpc.insecure_channel(addr)
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

    def CreateArktosNetwork(self, BuiltinsArktosMessage):
        resp = self.stub_builtins.CreateArktosNetwork(BuiltinsArktosMessage)
        return resp

    def CreateNetworkPolicy(self, BuiltinsNetworkPolicyMessage):
        resp = self.stub_builtins.CreateNetworkPolicy(
            BuiltinsNetworkPolicyMessage)
        return resp

    def CreateNamespace(self, BuiltinsNamespaceMessage):
        resp = self.stub_builtins.CreateNamespace(BuiltinsNamespaceMessage)
        return resp

    def UpdatePod(self, BuiltinsPodMessage):
        resp = self.stub_builtins.UpdatePod(BuiltinsPodMessage)
        return resp

    def UpdateService(self, BuiltinsServiceMessage):
        resp = self.stub_builtins.UpdateService(BuiltinsServiceMessage)
        return resp

    def UpdateNode(self, BuiltinsNodeMessage):
        resp = self.stub_builtins.UpdateNode(BuiltinsNodeMessage)
        return resp

    def UpdateArktosNetwork(self, BuiltinsArktosMessage):
        resp = self.stub_builtins.UpdateArktosNetwork(BuiltinsArktosMessage)
        return resp

    def UpdateNetworkPolicy(self, BuiltinsNetworkPolicyMessage):
        resp = self.stub_builtins.UpdateNetworkPolicy(
            BuiltinsNetworkPolicyMessage)
        return resp

    def UpdateNamespace(self, BuiltinsNamespaceMessage):
        resp = self.stub_builtins.UpdateNamespace(BuiltinsNamespaceMessage)
        return resp

    def ResumePod(self, BuiltinsPodMessage):
        resp = self.stub_builtins.ResumePod(BuiltinsPodMessage)
        return resp

    def ResumeService(self, BuiltinsServiceMessage):
        resp = self.stub_builtins.ResumeService(BuiltinsServiceMessage)
        return resp

    def ResumeNode(self, BuiltinsNodeMessage):
        resp = self.stub_builtins.ResumeNode(BuiltinsNodeMessage)
        return resp

    def ResumeArktosNetwork(self, BuiltinsArktosMessage):
        resp = self.stub_builtins.ResumeArktosNetwork(BuiltinsArktosMessage)
        return resp

    def ResumeNetworkPolicy(self, BuiltinsNetworkPolicyMessage):
        resp = self.stub_builtins.ResumeNetworkPolicy(
            BuiltinsNetworkPolicyMessage)
        return resp

    def ResumeNamespace(self, BuiltinsNamespaceMessage):
        resp = self.stub_builtins.ResumeNamespace(BuiltinsNamespaceMessage)
        return resp

    def DeleteNode(self, BuiltinsNodeMessage):
        resp = self.stub_builtins.DeleteNode(BuiltinsNodeMessage)
        return resp

    def DeleteService(self, BuiltinsServiceMessage):
        resp = self.stub_builtins.DeleteService(BuiltinsServiceMessage)
        return resp

    def DeletePod(self, BuiltinsPodMessage):
        resp = self.stub_builtins.DeletePod(BuiltinsPodMessage)
        return resp

    def DeleteNetworkPolicy(self, BuiltinsNetworkPolicyMessage):
        resp = self.stub_builtins.DeleteNetworkPolicy(
            BuiltinsNetworkPolicyMessage)
        return resp

    def DeleteNetworkPolicy(self, BuiltinsNetworkPolicyMessage):
        resp = self.stub_builtins.DeleteNetworkPolicy(
            BuiltinsNetworkPolicyMessage)
        return resp

    def DeleteNamespace(self, BuiltinsNamespaceMessage):
        resp = self.stub_builtins.DeleteNamespace(BuiltinsNamespaceMessage)
        return resp

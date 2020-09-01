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

droplet_opr = DropletOperator()
bouncer_opr = BouncerOperator()
endpoint_opr = EndpointOperator()
vpc_opr = VpcOperator()
logger = logging.getLogger()


class ProxyServer(ArktosNetworkServiceServicer, BuiltinsServiceServicer):

    def __init__(self):
        self.store = OprStore()
        config.load_incluster_config()
        self.obj_api = client.CustomObjectsApi()

    def CreatePod(self, request, context):
        spec = {
            'hostIP': request.ip,
            'name': request.name,
            'namespace': request.namespace,
            'tenant': '',
            'vpc': OBJ_DEFAULTS.default_ep_vpc,
            'net': OBJ_DEFAULTS.default_ep_net,
            'phase': request.phase,
            'interfaces': [{'name': 'eth0'}]
        }

        logger.info("Pod spec {}".format(spec))
        spec['vni'] = vpc_opr.store_get(spec['vpc']).vni
        spec['droplet'] = droplet_opr.store_get_by_ip(spec['hostIP'])
        if request.phase != 'Pending':
            return
        interfaces = endpoint_opr.init_simple_endpoint_interfaces(
            spec['hostIP'], spec)
        endpoint_opr.create_simple_endpoints(interfaces, spec)

    def CreateNode(self, request, context):
        droplet_opr.create_droplet(request.ip)

    def CreateService(self, request, context):
        logger.info("Create scaled endpoint {}.".format(request.name))
        ep = Endpoint(request.name, endpoint_opr.obj_api, endpoint_opr.store)
        ip = request.ip
        ep.set_vni(OBJ_DEFAULTS.default_vpc_vni)
        ep.set_vpc(OBJ_DEFAULTS.default_ep_vpc)
        ep.set_net(OBJ_DEFAULTS.default_ep_net)
        ep.set_ip(ip)
        ep.set_mac(endpoint_opr.rand_mac())
        ep.set_type(OBJ_DEFAULTS.ep_type_scaled)
        ep.set_status(OBJ_STATUS.ep_status_init)
        ep.create_obj()

    def CreateServiceEndpoint(self, request, context):
        ep = self.__update_scaled_endpoint_backend(
            request.name, request.namespace, request.ports, request.backends)
        if ep:
            if not bouncer_opr.store.get_bouncers_of_net(ep.net):
                logger.error("Bouncers not yet ready")
            else:
                bouncer_opr.update_endpoint_with_bouncers(ep)

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

    def __update_scaled_endpoint_backend(self, name, namespace, ports, backend_ips):
        ep = endpoint_opr.store.get_ep(name)
        if ep is None:
            return None
        backends = set()
        for b in backend_ips:
            backends.add(b)
        ports_map = {}
        for port in ports:
            ports_map[ports.frontend_port] = []
            ports_map[ports.frontend_port].append(port.frontend_port)
            proto = port.proto
            if proto == "TCP":
                ports_map[ports.frontend_port].append(CONSTANTS.IPPROTO_TCP)
            if proto == "UDP":
                ports_map[ports.frontend_port].append(CONSTANTS.IPROTO_UDP)
        ep.set_backends(list(backends))
        ep.set_ports(sorted(ports_map.items()))  # Sorted by frontend ports
        endpoint_opr.store_update(ep)
        logger.info(
            "Update scaled endpoint {} with backends: {}".format(name, backends))
        return endpoint_opr.store.get_ep(name)


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

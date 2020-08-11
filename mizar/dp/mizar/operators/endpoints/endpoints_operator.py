# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>

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
import random
from kubernetes import client, config
from mizar.obj.endpoint import Endpoint
from mizar.obj.bouncer import Bouncer
from mizar.common.constants import *
from mizar.common.common import *
from mizar.store.operator_store import OprStore
from mizar.proto.interface_pb2 import *
from mizar.daemon.interface_service import InterfaceServiceClient
import uuid

logger = logging.getLogger()


class EndpointOperator(object):
    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super(EndpointOperator, cls).__new__(cls)
            cls._init(cls, **kwargs)
        return cls._instance

    def _init(self, **kwargs):
        logger.info(kwargs)
        self.store = OprStore()
        config.load_incluster_config()
        self.obj_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()

    def query_existing_endpoints(self):
        def list_endpoint_obj_fn(name, spec, plurals):
            logger.info("Bootstrapped {}".format(name))
            ep = Endpoint(name, self.obj_api, self.store, spec)
            if ep.status == OBJ_STATUS.ep_status_provisioned:
                self.store_update(ep)

        kube_list_obj(self.obj_api, RESOURCES.endpoints, list_endpoint_obj_fn)

    def get_endpoint_tmp_obj(self, name, spec):
        return Endpoint(name, self.obj_api, None, spec)

    def get_endpoint_stored_obj(self, name, spec):
        return Endpoint(name, self.obj_api, self.store, spec)

    def set_endpoint_provisioned(self, ep):
        ep.set_status(OBJ_STATUS.ep_status_provisioned)
        ep.update_obj()

    def store_update(self, ep):
        self.store.update_ep(ep)

    def store_delete(self, ep):
        self.store.delete_ep(ep.name)

    def store_get(self, name):
        return self.store.get_ep(name)

    def on_endpoint_delete(self, body, spec, **kwargs):
        logger.info("on_endpoint_delete {}".format(spec))

    def on_endpoint_provisioned(self, body, spec, **kwargs):
        name = kwargs['name']
        logger.info("on_endpoint_provisioned {}".format(spec))
        ep = Endpoint(name, self.obj_api, self.store, spec)
        self.store.update_ep(ep)

    def update_bouncer_with_endpoints(self, bouncer):
        eps = self.store.get_eps_in_net(bouncer.net).values()
        bouncer.update_eps(eps)

    def update_endpoints_with_bouncers(self, bouncer):
        eps = list(self.store.get_eps_in_net(bouncer.net).values())
        for ep in eps:
            if ep.type == OBJ_DEFAULTS.ep_type_simple or ep.type == OBJ_DEFAULTS.ep_type_host:
                ep.update_bouncers({bouncer.name: bouncer})

    def create_scaled_endpoint(self, name, spec, namespace="default"):
        logger.info("Create scaled endpoint {} spec {}".format(name, spec))
        ep = Endpoint(name, self.obj_api, self.store)
        ip = spec['clusterIP']
        # If not provided in Pod, use defaults
        # TODO: have it pod :)
        ep.set_vni(OBJ_DEFAULTS.default_vpc_vni)
        ep.set_vpc(OBJ_DEFAULTS.default_ep_vpc)
        ep.set_net(OBJ_DEFAULTS.default_ep_net)
        ep.set_ip(ip)
        ep.set_mac(self.rand_mac())
        ep.set_type(OBJ_DEFAULTS.ep_type_scaled)
        ep.set_status(OBJ_STATUS.ep_status_init)
        ep.create_obj()
        self.annotate_builtin_endpoints(name, namespace)

    def create_gw_endpoint(self, name, ip):
        logger.info("Create gw endpoint")
        ep = Endpoint(name, self.obj_api, self.store)
        ep.set_vni(OBJ_DEFAULTS.default_vpc_vni)
        ep.set_vpc(OBJ_DEFAULTS.default_ep_vpc)
        ep.set_net(OBJ_DEFAULTS.default_ep_net)
        ep.set_mac(self.rand_mac())
        ep.set_ip(ip)
        ep.set_type(OBJ_DEFAULTS.ep_type_gateway)
        ep.set_status(OBJ_STATUS.ep_status_init)
        return ep

    def annotate_builtin_endpoints(self, name, namespace='default'):
        get_body = True
        while get_body:
            endpoint = kube_get_endpoints(self.core_api, name, namespace)
            if not endpoint or not endpoint.metadata or not endpoint.metadata.annotations:
                return
            endpoint.metadata.annotations[OBJ_DEFAULTS.mizar_service_annotation_key] = OBJ_DEFAULTS.mizar_service_annotation_val
            try:
                self.core_api.patch_namespaced_endpoints(
                    name=name,
                    namespace=namespace,
                    body=endpoint)
                get_body = False
            except:
                logger.debug(
                    "Retry updating annotating endpoints {}".format(name))
                get_body = True

    def delete_scaled_endpoint(self, ep):
        logger.info("Delete scaled endpoint {}".format(ep.name))
        ep.delete_obj()

    def rand_mac(self):
        return "a5:5b:00:%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )

    def update_scaled_endpoint_backend(self, name, spec):
        ep = self.store.get_ep(name)
        if ep is None:
            return None
        backends = set()
        backend_ports = set()
        for s in spec:
            if "addresses" in s:
                for a in s['addresses']:
                    backends.add(a['ip'])
            if "ports" in s:
                for p in s['ports']:
                    backend_ports.add(str(p['port']))
        ep.set_backends(list(backends))
        ep.set_backend_ports(list(backend_ports))
        self.store_update(ep)
        logger.info(
            "Update scaled endpoint {} with backends: {}".format(name, backends))
        return self.store.get_ep(name)

    def delete_endpoints_from_bouncers(self, bouncer):
        eps = self.store.get_eps_in_net(bouncer.net).values()
        bouncer.delete_eps(eps)

    def delete_bouncer_from_endpoints(self, bouncer):
        eps = self.store.get_eps_in_net(bouncer.net).values()
        for ep in eps:
            ep.update_bouncers(set([bouncer]), False)

    def produce_simple_endpoint_interface(self, ep):
        """
        Constructs the final interface message and call the ProduceInterface rpc
        on the endpoint's droplet
        """
        interface_address = InterfaceAddress(version="4",
                                             ip_address=ep.get_ip(),
                                             ip_prefix=ep.get_prefix(),
                                             gateway_ip=ep.get_gw(),
                                             mac=ep.get_mac(),
                                             tunnel_id=ep.get_tunnel_id())
        interface = self.store_get(ep.name).interface

        # from the droplet operator
        droplet = SubstrateAddress(
            version="4",
            ip_address=ep.get_droplet_ip(), mac=ep.get_droplet_mac())

        # list of bouncers
        bouncers = []
        for bouncer in ep.bouncers.values():
            bouncers.append(SubstrateAddress(
                version="4", ip_address=bouncer.ip, mac=bouncer.mac))

        interfaces_list = [Interface(
            interface_id=interface.interface_id,
            interface_type=interface.interface_type,
            pod_provider=interface.pod_provider,
            veth=interface.veth,
            address=interface_address,
            droplet=droplet,
            bouncers=bouncers,
            status=interface.status
        )]

        if ep.type == OBJ_DEFAULTS.ep_type_host:
            interfaces_list[0].status = InterfaceStatus.consumed
            interfaces = InterfaceServiceClient(
                ep.get_droplet_ip()).ActivateHostInterface(interfaces_list[0])
        else:
            interfaces = InterfaceServiceClient(
                ep.get_droplet_ip()).ProduceInterfaces(InterfacesList(interfaces=interfaces_list))

        # At this point Mizar has provisioned the network
        # TODO (cathy): mark the pod network as ready! Shall it be here or in
        # the pod builtin wf.
        logger.info("Produced {}".format(interfaces))

    def create_simple_endpoints(self, interfaces, spec):
        """
        Create a simple endpoint object (calling the API operator)
        """
        for interface in interfaces.interfaces:
            logger.info("Create simple endpoint {}".format(interface))
            name = get_itf_name(interface.interface_id)
            ep = Endpoint(name, self.obj_api, self.store)

            ep.set_type(OBJ_DEFAULTS.ep_type_simple)
            ep.set_status(OBJ_STATUS.ep_status_init)

            ep.set_vni(spec['vni'])
            ep.set_vpc(spec['vpc'])
            ep.set_net(spec['net'])

            ep.set_mac(interface.address.mac)
            ep.set_veth_name(interface.veth.name)
            ep.set_veth_peer(interface.veth.peer)
            ep.set_droplet(spec['droplet'].name)

            ep.set_droplet_ip(spec['droplet'].ip)
            ep.set_droplet_mac(spec['droplet'].mac)
            ep.set_interface(interface)
            ep.create_obj()
            self.store_update(ep)

    def create_host_endpoint(self, ip, droplet, interfaces):
        for interface in interfaces.interfaces:
            logger.info("Create host endpoint {}".format(interface))
            name = get_itf_name(interface.interface_id)
            ep = Endpoint(name, self.obj_api, self.store)

            ep.set_type(OBJ_DEFAULTS.ep_type_host)
            ep.set_status(OBJ_STATUS.ep_status_init)

            ep.set_vni(OBJ_DEFAULTS.default_vpc_vni)
            ep.set_vpc(OBJ_DEFAULTS.default_ep_vpc)
            ep.set_net(OBJ_DEFAULTS.default_ep_net)

            ep.set_mac(interface.address.mac)
            ep.set_veth_name(interface.veth.name)
            ep.set_veth_peer(interface.veth.peer)
            ep.set_droplet(droplet.name)
            ep.droplet_obj = droplet
            ep.set_ip(ip)
            ep.set_prefix(OBJ_DEFAULTS.default_host_ep_prefix)

            ep.set_droplet_ip(droplet.ip)
            ep.set_droplet_mac(droplet.mac)
            ep.set_interface(interface)
            ep.create_obj()
            self.store_update(ep)

    def init_simple_endpoint_interfaces(self, worker_ip, spec):
        """
        Construct the interface message and call the InitializeInterfaces gRPC on
        the hostIP
        """
        logger.info("init_simple_endpoint_interface {}".format(worker_ip))
        pod_id = PodId(k8s_pod_name=spec['name'],
                       k8s_namespace=spec['namespace'],
                       k8s_pod_tenant=spec['tenant'])

        interfaces_list = []

        for itf in spec['interfaces']:
            interface_id = InterfaceId(
                pod_id=pod_id, interface=itf['name'])

            itf_name = get_pod_name(pod_id) + '-' + itf['name']
            local_id = str(uuid.uuid3(uuid.NAMESPACE_URL, itf_name))[0:8]
            veth_name = "eth-" + local_id
            veth_peer = "veth-" + local_id
            veth = VethInterface(name=veth_name, peer=veth_peer)

            interfaces_list.append(Interface(
                interface_id=interface_id,
                interface_type=InterfaceType.veth,
                pod_provider=PodProvider.K8S,
                veth=veth,
                status=InterfaceStatus.init
            ))

        interfaces = InterfacesList(interfaces=interfaces_list)

        # The Interface service will create the veth peers for the interface and
        # allocate the mac addresses for us.
        return InterfaceServiceClient(worker_ip).InitializeInterfaces(interfaces)

    def init_host_endpoint_interfaces(self, droplet):
        interfaces_list = []
        pod_id = PodId(k8s_pod_name=droplet.name,
                       k8s_namespace="default",
                       k8s_pod_tenant="")
        interface_id = InterfaceId(
            pod_id=pod_id, interface="hostep")
        veth_name = "eth-hostep"
        veth_peer = "veth-hostep"
        veth = VethInterface(name=veth_name, peer=veth_peer)

        interfaces_list.append(Interface(
            interface_id=interface_id,
            interface_type=InterfaceType.veth,
            pod_provider=PodProvider.K8S,
            veth=veth,
            status=InterfaceStatus.init
        ))
        interfaces = InterfacesList(interfaces=interfaces_list)
        return InterfaceServiceClient(droplet.ip).InitializeInterfaces(interfaces)

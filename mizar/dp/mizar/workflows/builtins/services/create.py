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
from kubernetes import client
from mizar.common.workflow import *
from mizar.common.common import kube_patch_service
from mizar.dp.mizar.operators.bouncers.bouncers_operator import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.nets.nets_operator import *
from mizar.dp.mizar.operators.vpcs.vpcs_operator import *

logger = logging.getLogger()

endpoints_opr = EndpointOperator()
bouncers_opr = BouncerOperator()
net_opr = NetOperator()
vpc_opr = VpcOperator()


class k8sServiceCreate(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        net = net_opr.store.get_net(OBJ_DEFAULTS.default_ep_net)
        if self.param.body['metadata'].get('annotations'):
            if self.param.body['metadata'].get('annotations').get(OBJ_DEFAULTS.mizar_ep_vpc_annotation):
                vpc_name = self.param.body['metadata'].get(
                    'annotations').get(OBJ_DEFAULTS.mizar_ep_vpc_annotation)
                vpc = vpc_opr.store_get(vpc_name)
                if not vpc:
                    self.raise_temporary_error(
                        "VPC {} for service {} does not exist!".format(vpc_name, self.param.name))
                if self.param.body['metadata'].get('annotations').get(OBJ_DEFAULTS.mizar_ep_subnet_annotation):
                    subnet_name = self.param.body['metadata'].get(
                        'annotations').get(OBJ_DEFAULTS.mizar_ep_subnet_annotation)
                    subnet = net_opr.store.get_net(subnet_name)
                    if subnet.vpc != vpc_name:
                        self.raise_temporary_error("Subnet {} of service {} does not belong to VPC {}".format(
                            subnet_name, self.param.name, vpc_name))
                    if not subnet:
                        self.raise_temporary_error(
                            "Subnet {} of service {} does not exist!".format(subnet_name, self.param.name))
                else:
                    subnets = list(net_opr.store.get_nets_in_vpc(vpc_name))
                    if subnets:
                        subnet_name = subnets[0]
                        logger.info("Subnet specified, allocating service {} in subnet {} for VPC {}".format(
                            self.param.name, subnet_name, vpc_name))
                    else:
                        self.raise_temporary_error(
                            "VPC {} has no subnets to allocate service {}!".format(vpc_name, self.param.name))
                net = net_opr.store.get_net(subnet_name)
        namespace = self.param.body['metadata']['namespace']
        tenant = self.param.extra.get('tenant', '')
        name = self.param.name + "-{}-{}".format(namespace, tenant)
        logger.info("Service name is {}".format(name))
        if not net:
            self.raise_temporary_error(
                "Task: {} Net not yet created.".format(self.__class__.__name__))
        logger.info("Creating scaled endpoint in subnet: {}.".format(net.name))
        ep = endpoints_opr.create_scaled_endpoint(
            self.param.name, name, self.param.spec, net, self.param.extra, self.param.body['metadata']['namespace'])
        self.param.return_message = ep.ip
        self.finalize()


class k8sEndpointsUpdate(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        if 'subsets' not in self.param.body and not self.param.extra:
            return
        namespace = self.param.body["metadata"]["namespace"]
        tenant = self.param.body['metadata'].get('tenant', '')
        name = self.param.name + "-{}-{}".format(namespace, tenant)
        logger.info("Endpoint name is {}".format(name))
        ep = endpoints_opr.store.get_ep(name)
        if not ep:
            self.raise_temporary_error(
                "Task: {} Endpoint: {} Not yet created.".format(self.__class__.__name__, name))

        if self.param.extra:
            endpoints_opr.update_scaled_endpoint_backend_service_json(
                self.param.name, name, namespace, self.param.extra["ports"], self.param.extra["backend_ips"])
        else:
            ep = endpoints_opr.update_scaled_endpoint_backend(
                self.param.name, name, namespace, self.param.body['subsets'])
        if ep:
            if not bouncers_opr.store.get_bouncers_of_net(ep.net):
                self.raise_temporary_error(
                    "Task: {} Endpoint: {} bouncers not yet provisioned.".format(self.__class__.__name__, ep.name))
            bouncers_opr.update_endpoint_with_bouncers(ep, self)
        self.finalize()

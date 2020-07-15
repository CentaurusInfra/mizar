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
from mizar.common.workflow import *
from mizar.dp.mizar.operators.droplets.droplets_operator import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.vpcs.vpcs_operator import *
from mizar.common.constants import *

logger = logging.getLogger()

droplet_opr = DropletOperator()
endpoint_opr = EndpointOperator()
vpc_opr = VpcOperator()


class k8sPodCreate(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        # name in self.param.body['metadata']['name']
        # namespace in self.param.body['metadata']['namespace']
        # label in self.param.body['metadata']['label']
        # annotations in self.param.body['metadata']['annotations']

        # logger.info("name: {}".format(self.param.body['metadata']['name']))
        # logger.info("namespace: {}".format(
        #     self.param.body['metadata']['namespace']))
        # logger.info("label: {}".format(self.param.body['metadata']['labels']))
        # logger.info("annotations: {}".format(
        #     self.param.body['metadata']['annotations']))
        # logger.info("hostNetwork: {}".format(
        #     self.param.spec.get('hostNetwork', 'False')))
        # logger.info("hostIP: {}".format(self.param.body['status']['hostIP']))
        # logger.info("phase: {}".format(self.param.body['status']['phase']))
        # logger.info("podIPs: {}".format(self.param.body['status']['podIPs']))

        spec = {
            'hostIP': self.param.body['status']['hostIP'],
            'name': self.param.body['metadata']['name'],
            'namespace': self.param.body['metadata']['namespace'],
            'tenant': '',
            # TODO (Cathy) in case of arktos
            # get VPC and net information from annotation
            'vpc': OBJ_DEFAULTS.default_ep_vpc,
            'net': OBJ_DEFAULTS.default_ep_net,
            'phase': self.param.body['status']['phase'],
            # TODO (Cathy) in case of arktos get list of interfaces to create on
            # the host (names)
            'interfaces': [{'name': 'eth0'}]
        }

        logger.info("Pod spec {}".format(spec))
        spec['vni'] = vpc_opr.store_get(spec['vpc']).vni
        spec['droplet'] = droplet_opr.store_get_by_ip(spec['hostIP'])

        # TODO (cathy): make sure not to trigger init or create simple endpoint
        # if Arktos network is already marked ready
        if spec['phase'] != 'Pending':
            self.finalize()
            return

        # Init all interfaces on the host
        interfaces = endpoint_opr.init_simple_endpoint_interfaces(
            spec['hostIP'], spec)

        # Create the corresponding simple endpoint objects
        endpoint_opr.create_simple_endpoints(interfaces, spec)

        # TODO (cathy): in Arktos shall we mark the pod network ready here?
        self.finalize()

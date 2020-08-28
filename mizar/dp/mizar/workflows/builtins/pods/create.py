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
import json
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

        if "hostIP" not in self.param.body['status']:
            self.raise_temporary_error("Pod spec not ready.")
        spec = {
            'hostIP': self.param.body['status']['hostIP'],
            'name': self.param.body['metadata']['name'],
            'type': COMPUTE_PROVIDER.k8s,
            'namespace': self.param.body['metadata'].get('namespace', 'default'),
            'tenant': self.param.body['metadata'].get('tenant', ''),
            'vpc': self.param.body['metadata'].get('labels', {}).get(
                    'arktos.futurewei.com/network', OBJ_DEFAULTS.default_ep_vpc),
            'net': OBJ_DEFAULTS.default_ep_net,
            'phase': self.param.body['status']['phase'],
            'readiness': self.param.body['metadata'].get('annotations', {}).get(
                    'arktos.futurewei.com/network-readiness', ''),
            'interfaces': [{'name': 'eth0'}]
        }

        logger.info("Pod spec {}".format(spec))
        spec['vni'] = vpc_opr.store_get(spec['vpc']).vni
        spec['droplet'] = droplet_opr.store_get_by_ip(spec['hostIP'])

        if 'arktos.futurewei.com/network' in self.param.body['metadata'].get('labels', {}):
            spec['type'] =  COMPUTE_PROVIDER.arktos

        # Example: arktos.futurewei.com/nic: [{"name": "eth0", "ip": "10.10.1.12", "subnet": "net1"}]
        # all three fields are optional. Each item in the list corresponding to an endpoint
        # which represents a network interface for a pod
        if 'arktos.futurewei.com/nic' in self.param.body['metadata'].get('annotations', {}):
            net_config = self.param.body['metadata']['annotations']['arktos.futurewei.com/nic']
            configs = json.loads(net_config)
            spec['interfaces'] = configs

        # make sure not to trigger init or create simple endpoint
        # if Arktos network is already marked ready
        if spec['type'] ==  COMPUTE_PROVIDER.arktos and spec['readiness'] == 'true':
            self.finalize()
            return

        if spec['phase'] != 'Pending':
            self.finalize()
            return
        # Preexisting pods triggered when droplet objects are not yet created.
        if not spec['droplet']:
            self.raise_temporary_error("Droplet not yet created.")

        # Init all interfaces on the host
        interfaces = endpoint_opr.init_simple_endpoint_interfaces(
            spec['hostIP'], spec)

        # Create the corresponding simple endpoint objects
        endpoint_opr.create_simple_endpoints(interfaces, spec)

        ## CNI interface has builtin synchronization, do not need trigger
        if 'arktos.futurewei.com/network' in self.param.body['metadata'].get('labels', {}):
            endpoint_opr.annotate_builtin_pods(spec['name'], spec['namespace'])
        self.finalize()

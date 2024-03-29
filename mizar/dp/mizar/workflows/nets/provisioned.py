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
from mizar.dp.mizar.operators.nets.nets_operator import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.droplets.droplets_operator import *
from mizar.dp.mizar.operators.vpcs.vpcs_operator import *
logger = logging.getLogger()


nets_opr = NetOperator()
endpoints_opr = EndpointOperator()
droplets_opr = DropletOperator()
vpcs_opr = VpcOperator()


class NetProvisioned(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        net = nets_opr.store.get_net(self.param.name)
        if not net:
            logger.info("NetProvisioned: Net not found in store. Creating new network object for {}".format(
                self.param.name))
            net = nets_opr.get_net_stored_obj(self.param.name, self.param.spec)
        logger.info("Provisioned Net ip is {}".format(net.ip))
        for d in self.param.diff:
            if d[0] == 'change':
                self.process_change(net=net, field=d[1], old=d[2], new=d[3])
        vpc = vpcs_opr.store.get_vpc(net.vpc)
        for droplet in list(droplets_opr.store.get_all_droplets()):
            logger.info("Net: Available droplets for vpc {}: {}".format(
                vpc.name, droplets_opr.store.droplets_store.keys()))
            if vpc.name not in droplets_opr.store_get_vpc_to_droplet(droplet):
                logger.info("Net: Creating host endpoint for vpc {} on droplet {}".format(
                    vpc.name, droplet.ip))
                droplet.interfaces = endpoints_opr.init_host_endpoint_interfaces(
                    droplet,
                    "{}-{}".format(OBJ_DEFAULTS.host_ep_name,
                                   vpc.get_vni()),
                    "{}-{}".format(OBJ_DEFAULTS.host_ep_veth_name,
                                   vpc.get_vni()),
                    "{}-{}".format(OBJ_DEFAULTS.host_ep_peer_name,
                                   vpc.get_vni()),
                    self
                )
                droplets_opr.store_update(droplet)
                endpoints_opr.create_host_endpoint(
                    droplet.ip, droplet, droplet.interfaces,
                    vpc,
                    net
                )
            else:
                logger.info("Net: Host endpoint already created for vpc {} on droplet {}".format(
                    vpc.name, droplet.ip))
        self.finalize()

    def process_change(self, net, field, old, new):
        logger.info("diff_field:{}, from:{}, to:{}".format(field, old, new))
        if field[0] == 'spec' and field[1] == 'bouncers':
            return nets_opr.process_bouncer_change(net, int(old), int(new))

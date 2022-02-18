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
from mizar.dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

droplets_opr = DropletOperator()
endpoint_opr = EndpointOperator()
vpcs_opr = VpcOperator()
nets_opr = NetOperator()


class DropletProvisioned(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        droplet = droplets_opr.get_droplet_stored_obj(
            self.param.name, self.param.spec)
        for vpc in vpcs_opr.store.get_all_vpcs():
            if droplet.name not in droplets_opr.store.vpc_droplet_store[vpc.name]:
                if nets_opr.store.get_nets_in_vpc(vpc):
                    subnet = list(
                        nets_opr.store.get_nets_in_vpc(vpc).values())[0]
                    logger.info("Droplet: Creating host endpoint for vpc {} on droplet {}".format(
                        vpc.name, droplet.ip))
                    droplet.interfaces = endpoint_opr.init_host_endpoint_interfaces(
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
                    host_ep = endpoint_opr.create_host_endpoint(
                        droplet.ip, droplet, droplet.interfaces,
                        vpc.get_name(),
                        subnet
                    )
                    endpoint_opr.produce_simple_endpoint_interface(
                        host_ep, self)
                    droplets_opr.store_update_vpc_to_droplet(vpc, droplet)
                else:
                    self.raise_temporary_error(
                        "Host ep creation failed: no subnet created yet for VPC {} node ip {}".format(vpc.get_name(), droplet.ip))
            else:
                logger.info("Droplet: Host endpoint already created for vpc {} on droplet {}".format(
                    vpc.name, droplet.ip))
        self.finalize()

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
from mizar.common.constants import *
from mizar.dp.mizar.operators.bouncers.bouncers_operator import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.nets.nets_operator import *
from mizar.dp.mizar.operators.droplets.droplets_operator import *
from mizar.dp.mizar.operators.vpcs.vpcs_operator import *

logger = logging.getLogger()

bouncers_opr = BouncerOperator()
endpoints_opr = EndpointOperator()
nets_opr = NetOperator()
droplets_opr = DropletOperator()
vpcs_opr = VpcOperator()


class EndpointCreate(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        ep = endpoints_opr.get_endpoint_stored_obj(
            self.param.name, self.param.spec)
        ep.droplet_obj = droplets_opr.store.get_droplet(ep.droplet)
        if ep.type in OBJ_DEFAULTS.droplet_eps and not ep.droplet_obj:
            self.raise_temporary_error(
                "Task: {} Endpoint: {} Droplet Object {} not ready. ".format(self.__class__.__name__, ep.name, ep.droplet))
        vpc = vpcs_opr.store.get_vpc(ep.vpc)
        nets_opr.allocate_endpoint(ep, vpc)
        bouncers_opr.update_endpoint_with_bouncers(ep, self)
        if ep.type == OBJ_DEFAULTS.ep_type_simple or ep.type == OBJ_DEFAULTS.ep_type_host:
            if ep.type == OBJ_DEFAULTS.ep_type_host:
                logger.info("Activate host interface for vpc {} on droplet {}".format(
                    ep.vpc, ep.droplet_obj.ip))
                droplets_opr.store_update_vpc_to_droplet(vpc, ep.droplet_obj)
            itf = endpoints_opr.produce_simple_endpoint_interface(ep, self)
            logger.info(
                "Endpoint Create: Endpoint {} produced interface {}".format(ep.name, itf))
        endpoints_opr.set_endpoint_provisioned(ep)
        self.finalize()

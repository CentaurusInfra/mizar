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
from mizar.dp.mizar.operators.bouncers.bouncers_operator import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

endpoints_opr = EndpointOperator()
bouncers_opr = BouncerOperator()


class k8sServiceCreate(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        endpoints_opr.create_scaled_endpoint(
            self.param.name, self.param.spec, self.param.body['metadata']['namespace'])
        self.finalize()


class k8sEndpointsUpdate(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        if 'subsets' not in self.param.body:
            return
        namespace = self.param.body["metadata"]["namespace"]
        ep = endpoints_opr.update_scaled_endpoint_backend(
            self.param.name, namespace, self.param.body['subsets'])
        if ep:
            if not bouncers_opr.store.get_bouncers_of_net(ep.net):
                self.raise_temporary_error(
                    "Task: {} Endpoint: {} bouncers not yet provisioned.".format(self.__class__.__name__, ep.name))
            bouncers_opr.update_endpoint_with_bouncers(ep)
        self.finalize()

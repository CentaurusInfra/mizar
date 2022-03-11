# SPDX-License-Identifier: MIT
# Copyright (c) 2022 The Authors.

# Authors: The Mizar Team

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

import unittest
from teste2e.common.k8s import *
from teste2e.common.helper import *


class test_basic_vpc(unittest.TestCase):

    def setUp(self):
        self.test_name = "test-basic-vpc-"
        self.cluster = k8sCluster()
        self.api = k8sApi()
        vpc_name = "vpc1"
        subnet_name = "net1"
        subnet2_name = "net2"
        self.vpc = self.api.create_vpc(vpc_name, "12.0.0.0", "8")
        vpc = self.api.get_vpc(vpc_name)
        self.subnet1 = self.api.create_net(
            subnet_name, "12.2.0.0", "16", vpc_name, vpc["vni"])
        self.subnet2 = self.api.create_net(
            subnet2_name, "12.4.0.0", "16", vpc_name, vpc["vni"])
        self.api.get_net(subnet_name)
        self.api.get_net(subnet2_name)
        self.ep1 = self.api.create_pod(
            self.test_name + "ep1", vpc_name, subnet_name)
        self.ep2 = self.api.create_pod(
            self.test_name + "ep2", vpc_name, subnet_name)
        self.ep3 = self.api.create_pod(
            self.test_name + "ep3", vpc_name, subnet2_name)
        self.ep4 = self.api.create_pod(self.test_name + "ep4", vpc_name, None)

        # DISABLED scaled ep tests
        # self.ep11 = self.api.create_pod(self.test_name + "ep11", vpc_name, subnet_name)
        # self.sep1 = self.api.create_service(self.test_name + "sep1", vpc_name, subnet_name)
        # self.sep1.add_endpoint(self.test_name + "ep33", vpc_name, subnet_name)

    def tearDown(self):
        pass

    def test_basic_vpc(self):
        pass
        do_common_tests(self, self.ep1, self.ep2)
        logger.info("Cross Network Comunication")
        do_common_tests(self, self.ep1, self.ep3)
        logger.info("Endpoint allocated in default subnet")
        do_common_tests(self, self.ep2, self.ep4)
        # DISABLED scaled ep tests
        # self.assertTrue(self.ep11.do_curl_hostname(self.sep1, "scaled"))
        # self.assertTrue(self.ep11.do_tcp_hostname(self.sep1, "scaled"))
        # self.assertTrue(self.ep11.do_udp_hostname(self.sep1, "scaled"))

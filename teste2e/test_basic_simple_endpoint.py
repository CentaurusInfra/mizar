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


class test_basic_simple_endpoint(unittest.TestCase):

    def setUp(self):
        # This test will use the default VPC and Net
        self.test_name = "test-basic-simple-endpoint-"
        self.cluster = k8sCluster()
        self.api = k8sApi()
        self.ep1 = self.api.create_pod(self.test_name + "ep1")
        self.ep2 = self.api.create_pod(self.test_name + "ep2")

    def tearDown(self):
        pass
        # logger.info("Tearing down endpoints....")
        # self.api.delete_pod(self.test_name + "ep1")
        # self.api.delete_pod(self.test_name + "ep2")

    def test_basic_simple_endpoint(self):
        do_common_tests(self, self.ep1, self.ep2)


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

    def tearDown(self):
        pass

    def test_basic_vpc(self):
        pass
        do_common_tests(self, self.ep1, self.ep2)
        logger.info("Cross Network Comunication")
        do_common_tests(self, self.ep1, self.ep3)
        logger.info("Endpoint allocated in default subnet")
        do_common_tests(self, self.ep2, self.ep4)

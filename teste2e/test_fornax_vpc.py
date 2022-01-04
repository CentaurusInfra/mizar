
import unittest
from mizar.common.constants import *
from teste2e.common.k8s import *
from teste2e.common.helper import *


class test_fornax_vpc(unittest.TestCase):

    def setUp(self):
        self.test_name = "test-fornax-vpc-"
        self.cluster = k8sCluster()
        self.api = k8sApi()
        vpc_name = "fornax-vpc1"
        vpc_name_with_empty_vni = "fornax-vpc2"
        vpc_name_with_dup_vni = "fornax-vpc3"
        vni = 10
        subnet_name = "fornax-net1"
        subnet2_name = "fornax-net2"
        self.vpc = self.api.create_vpc(vpc_name, "22.0.0.0", "8")
        
        # Test vpc creation with empty vni
        self.api.create_vpc(vpc_name_with_empty_vni, "23.0.0.0", "8", 1, None)
        vpc_with_empty_vni = self.api.get_vpc_with_status(vpc_name_with_empty_vni)
        self.assertNotEqual(vpc_with_empty_vni["vni"], None, "The vni shall not be none.")
        self.assertEqual(vpc_with_empty_vni["status"], OBJ_STATUS.obj_provisioned, "The status shall be provisioned.")

        # Test vpc creation with duplicate vni
        self.vpc_with_dup_vni = self.api.create_vpc(vpc_name_with_dup_vni, "24.0.0.0", "8", 1, vpc_with_empty_vni["vni"])
        vpc_with_dup_vni = self.api.get_vpc_with_status(vpc_name_with_dup_vni, OBJ_STATUS.vpc_status_duplicate_vni_error)
        self.assertEqual(vpc_with_dup_vni["status"], OBJ_STATUS.vpc_status_duplicate_vni_error, "The status shall be duplicate vni error.")

        vpc = self.api.get_vpc(vpc_name)

        self.subnet1 = self.api.create_net(
            subnet_name, "22.2.0.0", "16", vpc_name, vpc["vni"])
        self.subnet2 = self.api.create_net(
            subnet2_name, "22.4.0.0", "16", vpc_name, vpc["vni"], 1, False)
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

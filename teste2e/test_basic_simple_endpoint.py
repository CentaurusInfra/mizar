
import unittest
from teste2e.common.k8s import *
from teste2e.common.helper import *

class test_basic_simple_endpoint(unittest.TestCase):

    def setUp(self):
        # This test will use the default VPC and Net
        self.cluster = k8sCluster()
        self.api = k8sApi()
        self.ep1 = self.api.create_pod("ep1")
        self.ep2 = self.api.create_pod("ep2")

    def tearDown(self):
        logger.info("Tearing down endpoints....")
        self.api.delete_pod("ep1")
        self.api.delete_pod("ep2")

    def test_basic_simple_endpoint(self):
        do_common_tests(self, self.ep1, self.ep2)

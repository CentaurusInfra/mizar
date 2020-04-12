
import unittest
from teste2e.common.k8s import *
from teste2e.common.helper import *

class test_basic_scaled_endpoint(unittest.TestCase):

    def setUp(self):
        # This test will use the default VPC and Net
        self.cluster = k8sCluster()
        self.api = k8sApi()
        self.ep1 = self.api.create_pod("ep1")

        self.sep1 = self.api.create_service("sep1")
        self.ep3 = self.api.create_pod("ep2", scaledep="sep1")
        self.ep4 = self.api.create_pod("ep3", scaledep="sep1")

    def tearDown(self):
        logger.info("Tearing down endpoints....")
        self.api.delete_service("sep1")
        self.api.delete_pod("ep1")
        self.api.delete_pod("ep2")
        self.api.delete_pod("ep3")

    def test_basic_scaled_endpoint(self):
        self.assertTrue(self.ep1.do_ping(self.sep1))

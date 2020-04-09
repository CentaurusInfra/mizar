
import unittest
import os
from common import *
from k8s import *
from helper import *

class test_basic_switch(unittest.TestCase):

    def setUp(self):
        # This test will use the default VPC and Net
        self.cluster = k8sCluster()
        self.api = k8sApi()
        self.ep1 = self.api.create_pod("ep1")
        self.ep2 = self.api.create_pod("ep2")

    def tearDown(self):
        print("Tearing down endpoints....")
        self.api.delete_pod("ep1")
        self.api.delete_pod("ep2")

    def test_basic_switch(self):
        do_common_tests(self, self.ep1, self.ep2)

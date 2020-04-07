
import unittest
import os
from common import *
from k8s import *
import time

class test_basic_switch(unittest.TestCase):

    def setUp(self):
        # This test will use the default VPC and Net
        self.cluster = k8sCluster()
        self.api = k8sApi()
        self.ep1 = self.api.create_pod("ep6")
        self.ep2 = self.api.create_pod("ep7")

    def tearDown(self):
        logger.info("Tearing down the test")
        self.api.delete_pod("ep6")
        self.api.delete_pod("ep7")

    def test_basic_switch(self):
        logger.info("Testing testing testing :)")
        if self.ep1.ping(self.ep2.ip):
            logger.info("Success")
        if self.ep2.ping(self.ep1.ip):
            logger.info("Success")

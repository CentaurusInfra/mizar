
import unittest
import os
from common import *
from k8s import *


class test_basic_switch(unittest.TestCase):

    def setUp(self):
        logger.info("CWD {}".format(os.getcwd()))
        self.cluster = k8sCluster()
        self.api = k8sApi()
        self.api.create_vpc("myvpc6", "20.0.0.0", "24", 3)
        self.api.create_net("mynet1", "20.2.0.0", "16", "myvpc6", 1)
        self.api.create_pod("ep1")
        self.api.pod_exec("ep1")
        self.api.create_pod("ep2")
        self.api.pod_exec("ep2")
    #	self.api.list_ip()

    def tearDown(self):
        logger.info("Tearing down the test")
        self.api.delete_vpc("myvpc6")
        self.api.delete_net("mynet1")

    def test_basic_switch(self):
        logger.info("Testing testing testing :)")


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
        #self.api.delete_pod("ep6")
        #self.api.delete_pod("ep7")

    def test_basic_switch(self):
        logger.info("Testing testing testing :)")
        if self.ep1.ping(self.ep2.ip):
            logger.info("Ping test from {} to {} Success".format(self.ep1.name, self.ep2.name))
        if self.ep2.ping(self.ep1.ip):
            logger.info("Ping test from {} to {} Success".format(self.ep2.name, self.ep1.name))
        if self.ep1.http(self.ep2.name):
            logger.info("Http test from {} to {} Success".format(self.ep1.name, self.ep2.name))
        if self.ep2.http(self.ep1.name):
            logger.info("Http test from {} to {} Success".format(self.ep2.name, self.ep1.name))
        if self.ep1.tcp(self.ep2.name):
            logger.info("TCP test from {} to {} Success".format(self.ep1.name, self.ep2.name))

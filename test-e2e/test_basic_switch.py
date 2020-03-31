
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
		# Create network

	def tearDown(self):
		logger.info("Tearing down the test")
		self.api.delete_vpc("myvpc6")
		# Delete the network

	def test_basic_switch(self):
		logger.info("Testing testing testing :)")

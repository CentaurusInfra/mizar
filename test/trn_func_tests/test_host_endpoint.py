from test.trn_controller.controller import controller
from test.trn_controller.droplet import droplet
from test.trn_controller.common import cidr
from test.trn_func_tests.helper import *
import unittest
from time import sleep


class test_host_endpoint(unittest.TestCase):

    def setUp(self):

        self.droplets = {
            "d1": droplet("d1"),
            "d2": droplet("d2"),
            "d3": droplet("d3"),
            "d4": droplet("d4"),
            "d5": droplet("d5"),
            "d6": droplet("d6"), }

        c = controller(self.droplets)
        c.create_vpc(3, cidr("16", "10.0.0.0"), ["d1"])
        c.create_network(3, 10, cidr("24", "10.0.0.0"), ["d2"])
        c.create_network(3, 20, cidr("24", "10.0.20.0"), ["d3"])

        self.ep1 = c.create_simple_endpoint(3, 10, "10.0.0.2", "d4")
        self.ep2 = c.create_simple_endpoint(3, 20, "10.0.20.2", "d5")
        self.ep_host = c.create_host_endpoint(3, 10, "10.0.0.3", "d6")

    def tearDown(self):
        pass

    def test_host_endpoint(self):
        logger.info(
            "{} Testing all endpoints can communicate! {}".format('='*20, '='*20))
        do_common_tests(self, self.ep1, self.ep2)
        do_common_tests(self, self.ep_host, self.ep1)
        do_common_tests(self, self.ep_host, self.ep2)
        do_check_failed_rpcs(self, self.droplets.values())

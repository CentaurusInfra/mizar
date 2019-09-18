# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.controller import controller
from test.trn_controller.droplet import droplet
from test.trn_controller.common import cidr
from test.trn_func_tests.helper import *
import unittest
from time import sleep


class test_switch_multi_vpc(unittest.TestCase):

    def setUp(self):
        # Testing the following basic scenario
        #
        # +------------+      +------------+
        # |    Left    |      |   Right    |
        # | +--------+ |      | +--------+ |
        # | |  ns0   | |      | |  ns1   | |
        # | |        | |      | |        | |
        # | +--------+ |      | +--------+ |
        # | | veth0  | |      | | veth0  | |
        # | |10.0.0.1| |      | |10.0.0.2| |
        # | +--------+ |      | +--------+ |
        # |      |     |      |      |     |
        # |      |     |      |      |     |
        # |      |     |      |      |     |
        # | +--------+ |      | +--------+ |
        # | |Transit | |      | |Transit | |
        # | | Agent  | |      | | Agent  | |
        # | | peer0  | |      | | peer1  | |
        # | +--------+ |      | +--------+ |
        # +------------+      +------------+
        # |Transit XDP |      |Transit XDP |
        # |    eth0    |      |    eth0    |
        # +------------+      +------------+
        #        |                   |
        #        |   +------------+  |
        #        |   |   Switch   |  |
        #        |   |            |  |
        #        +---+------------+--+
        #            |Transit XDP |
        #            |    eth0    |
        #            +------------+

        self.droplets = {
            "left": droplet("left"),
            "right": droplet("right"),
            "switch": droplet("switch"),
        }
        c = controller(self.droplets)

        c.create_vpc(3, cidr("16", "10.0.0.0"), [])
        c.create_network(3, 1, cidr("16", "10.0.0.0"), ["switch"])

        c.create_vpc(4, cidr("16", "20.0.0.0"), [])
        c.create_network(4, 2, cidr("16", "20.0.0.0"), ["switch"])

        self.ep1 = c.create_simple_endpoint(3, 1, "10.0.0.2", "left")
        self.ep2 = c.create_simple_endpoint(4, 2, "20.0.0.2", "left")

        self.ep3 = c.create_simple_endpoint(3, 1, "10.0.0.3", "right")
        self.ep4 = c.create_simple_endpoint(4, 2, "20.0.0.3", "right")

    def tearDown(self):
        pass

    def test_switch_multi_vpc(self):
        logger.info(
            "{} Testing two endpoints on a same VPC can communicate! {}".format('='*20, '='*20))
        do_ping_test(self, self.ep1, self.ep3)

        logger.info(
            "{} Testing two endpoints on a different VPC can NOT communicate! {}".format('='*20, '='*20))
        do_ping_fail_test(self, self.ep1, self.ep2)

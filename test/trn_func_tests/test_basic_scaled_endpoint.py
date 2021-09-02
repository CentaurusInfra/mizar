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


class test_basic_scaled_endpoint(unittest.TestCase):

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
            "d0": droplet("d0"),
            "d1": droplet("d1"),
            "d2": droplet("d2"),
            "d3": droplet("d3"),
            "d4": droplet("d4"),
            "d5": droplet("d5")
        }
        self.c = controller(self.droplets)

        self.c.create_vpc(3, cidr("16", "10.0.0.0"), [])
        self.c.create_network(3, 1, cidr("16", "10.0.0.0"), ["d0"])
        self.ep0 = self.c.create_simple_endpoint(3, 1, "10.0.0.2", "d0")
        self.ep1 = self.c.create_simple_endpoint(3, 1, "10.0.0.3", "d1")
        self.ep2 = self.c.create_simple_endpoint(3, 1, "10.0.0.4", "d2")
        self.ep3 = self.c.create_simple_endpoint(3, 1, "10.0.0.5", "d3")

        self.sep = self.c.create_scaled_endpoint(3, 1, "10.0.0.6", [self.ep2])

    def tearDown(self):
        pass

    def test_basic_scaled_endpoint(self):
        logger.info(
            "{} Testing two endpoints on a switch can communicate! {}".format('='*20, '='*20))
        self.ep2.do_httpd()
        self.ep3.do_httpd()

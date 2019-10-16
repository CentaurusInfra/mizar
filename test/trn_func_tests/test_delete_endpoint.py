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


class test_delete_endpoint(unittest.TestCase):

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
        self.ep_right = c.create_simple_endpoint(3, 1, "10.0.0.3", "right")
        # Clear all droplet update state before we create and delete ep_left
        self.droplets["switch"].clear_update_call_state()
        self.droplets["right"].clear_update_call_state()

        self.ep_left = c.create_simple_endpoint(3, 1, "10.0.0.2", "left")
        self.ep_left = c.delete_simple_endpoint(3, 1, "10.0.0.2", "left")

    def tearDown(self):
        pass

    def test_delete_endpoint(self):
        logger.info(
            "{} Testing endpoint properly deleted! {}".format('='*20, '='*20))
        do_validate_delete_test(
            self, self.droplets.values())

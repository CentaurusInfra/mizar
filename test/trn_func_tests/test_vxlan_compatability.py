# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
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


class test_vxlan_compatability(unittest.TestCase):

    def setUp(self):
        # Testing the basic scenario with multiple switches
        # +------------+     +------------+
        # |    left    |     |   right    |
        # | +--------+ |     | +--------+ |
        # | |  ns0   | |     | |  ns1   | |
        # | |        | |     | |        | |
        # | +--------+ |     | +--------+ |
        # | | veth0  | |     | | veth0  | |
        # | |10.0.0.1| |     | |10.0.0.2| |
        # | +--------+ |     | +--------+ |
        # |      |     |     |      |     |
        # |      |     |     |      |     |
        # |      |     |     |      |     |
        # | +--------+ |     | +--------+ |
        # | |Transit | |     | |Transit | |
        # | | Agent  | |     | | Agent  | |
        # | | peer0  | |     | | peer1  | |
        # | +--------+ |     | +--------+ |
        # +------------+     +------------+
        # |Transit XDP |     |Transit XDP |
        # |    eth0    |     |    eth0    |
        # +------------+     +------------+
        #        |                  ^
        #        |  +----------+    |
        #        |  | Switch1  |    |
        #        |  |  +-------+--+ |
        #        +->|  | Switch2  | |
        #           |  |          | |
        #           +--+          |-+
        #              |          |
        #              +----------+

        self.droplets = {
            "left": droplet("left"),
            "right": droplet("right"),
            "switch-1": droplet("switch-1"),
            "switch-2": droplet("switch-2")
        }
        c = controller(self.droplets)

        c.create_vpc(3, cidr("16", "10.0.0.0"), [])
        c.create_network(3, 1, cidr("16", "10.0.0.0"),
                         ["switch-1", "switch-2"])
        self.ep_left = c.create_simple_endpoint(3, 1, "10.0.0.2", "left")
        self.ep_right = c.create_simple_endpoint(3, 1, "10.0.0.3", "right")

        self.ep_vxlan_left = c.create_vxlan_endpoint(3, 1, "10.0.0.4", "left")
        self.ep_vxlan_right = c.create_vxlan_endpoint(
            3, 1, "10.0.0.5", "right")

    def tearDown(self):
        pass

    def test_vxlan_compatability(self):
        logger.info(
            "{} Testing two simple endpoints can communicate! {}".format('='*20, '='*20))
        do_common_tests(self, self.ep_left, self.ep_right)

        logger.info(
            "{} Testing two vxlan endpoints can communicate! {}".format('='*20, '='*20))
        do_common_tests(self, self.ep_vxlan_left, self.ep_vxlan_right)

        logger.info(
            "{} Testing vxlan endpoint can communicate with geneve endpoint! {}".format('='*20, '='*20))
        do_common_tests(self, self.ep_vxlan_left, self.ep_right)

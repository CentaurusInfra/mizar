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


class test_direct_path_vpc(unittest.TestCase):

    def setUp(self):
        self.droplets = {
            "left": droplet("left"),
            "right": droplet("right"),
            "switch": droplet("switch"),
            "switch2": droplet("switch2"),
            "router": droplet("router")
        }
        c = controller(self.droplets)

        c.create_vpc(3, cidr("16", "10.0.0.0"), ["router"])
        c.create_network(3, 1, cidr("24", "10.0.0.0"), ["switch"])
        self.ep_left = c.create_simple_endpoint(3, 1, "10.0.0.2", "left")
        c.create_network(3, 2, cidr("24", "10.0.20.0"), ["switch2"])
        self.ep_right = c.create_simple_endpoint(3, 2, "10.0.20.3", "right")

    def tearDown(self):
        pass

    def test_direct_path_vpc(self):
        logger.info(
            "{} Testing VPC direct path! {}".format('='*20, '='*20))
        do_validate_direct_path(self, self.ep_left,
                                self.ep_right, self.droplets["switch"], self.droplets["router"], self.droplets["switch2"])
        do_check_failed_rpcs(self, self.droplets.values())

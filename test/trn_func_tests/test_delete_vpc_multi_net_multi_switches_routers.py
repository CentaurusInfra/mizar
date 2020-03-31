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


class test_vpc_delete_multi_net_multi_switches_routers(unittest.TestCase):

    def setUp(self):

        self.droplets = {
            "d1": droplet("d1"),
            "d2": droplet("d2"),
            "d3": droplet("d3"),
            "d4": droplet("d4"),
            "d5": droplet("d5"),
            "switch-1": droplet("switch-1"),
            "switch-4": droplet("switch-4"),
            "router-1": droplet("router-1"),
            "router-2": droplet("router-2"),
        }

        self.c = controller(self.droplets)

        self.c.create_vpc(3, cidr("16", "10.0.0.0"),
                          ["router-1", "router-2", "d5"])

        self.c.create_network(3, 10, cidr("24", "10.0.0.0"),
                              ["switch-1", "d3", "d5"])

        self.c.create_network(3, 20, cidr("24", "10.20.0.0"),
                              ["switch-4", "d2", "d5"])

        self.ep1 = self.c.create_simple_endpoint(3, 10, "10.0.0.2", "d1")
        self.ep2 = self.c.create_simple_endpoint(3, 10, "10.0.0.3", "d2")

        self.ep3 = self.c.create_simple_endpoint(3, 20, "10.20.0.4", "d3")
        self.ep4 = self.c.create_simple_endpoint(3, 20, "10.20.0.5", "d4")
        self.ep5 = self.c.create_simple_endpoint(3, 20, "10.20.0.6", "d4")
        self.ep6 = self.c.create_simple_endpoint(3, 20, "10.20.0.7", "d5")
        self.ep7 = self.c.create_simple_endpoint(
            3, 20, "10.20.0.8", "router-1")
        self.ep8 = self.c.create_simple_endpoint(
            3, 20, "10.20.0.9", "router-2")
        self.ep7 = self.c.create_simple_endpoint(
            3, 20, "10.20.0.10", "switch-1")
        self.ep8 = self.c.create_simple_endpoint(
            3, 20, "10.20.0.11", "switch-4")
        self.c.delete_vpc(3)

    def test_delete_vpc_multi_net_multi_switches_routers(self):
        logger.info(
            "{} Testing vpc properly deleted! {}".format('='*20, '='*20))
        do_validate_delete_test(self, list(self.droplets.values()))
        do_check_failed_rpcs(self, self.droplets.values())

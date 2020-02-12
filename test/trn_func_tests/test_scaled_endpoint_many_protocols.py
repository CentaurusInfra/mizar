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


class test_scaled_endpoint_many_protocols(unittest.TestCase):

    def setUp(self):

        self.droplets = {
            "d0": droplet("d0"),
            "d1": droplet("d1"),
            "d2": droplet("d2"),
            "d3": droplet("d3"),
            "d4": droplet("d4"),
            "d5": droplet("d5"),
            "d6": droplet("d6")
        }
        self.c = controller(self.droplets)

        self.c.create_vpc(3, cidr("16", "10.0.0.0"), [])
        self.c.create_network(3, 1, cidr("16", "10.0.0.0"), ["d0"])
        self.ep0 = self.c.create_simple_endpoint(3, 1, "10.0.0.2", "d1")
        self.ep1 = self.c.create_simple_endpoint(3, 1, "10.0.0.3", "d2")
        self.ep2 = self.c.create_simple_endpoint(3, 1, "10.0.0.4", "d3")
        self.ep3 = self.c.create_simple_endpoint(3, 1, "10.0.0.5", "d4")
        self.ep4 = self.c.create_simple_endpoint(3, 1, "10.0.0.6", "d5")
        self.ep5 = self.c.create_simple_endpoint(3, 1, "10.0.0.7", "d6")

        self.sep_backend = [self.ep1, self.ep2, self.ep3, self.ep4, self.ep5]
        self.sep = self.c.create_scaled_endpoint(
            3, 1, "10.0.0.8", self.sep_backend)

    def tearDown(self):
        pass

    def test_scaled_endpoint_many_protocols(self):
        do_test_scaled_ep_basic(self, self.ep0, self.sep, self.sep_backend)
        do_check_failed_rpcs(self, self.droplets.values())

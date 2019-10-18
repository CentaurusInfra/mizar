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


class test_delete_one_at_a_time(unittest.TestCase):

    def setUp(self):
        # Testing the following multiple subnetwork scenario
        # +------------+      +------------+        +------------+      +------------+
        # |     D1     |      |     D2     |        |     D3     |      |     D4     |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # | |  ns1   | |      | |  ns2   | |        | |  ns3   | |      | |  ns4   | |
        # | |        | |      | |        | |        | |        | |      | |        | |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # | | veth0  | |      | | veth0  | |        | | veth0  | |      | | veth0  | |
        # | |10.0.0.1| |      | |10.0.0.2| |        | |20.0.0.1| |      | |20.0.0.2| |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # |      |     |      |      |     |        |      |     |      |      |     |
        # |      |     |      |      |     |        |      |     |      |      |     |
        # |      |     |      |      |     |        |      |     |      |      |     |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # | |Transit | |      | |Transit | |        | |Transit | |      | |Transit | |
        # | | Agent  | |      | | Agent  | |        | | Agent  | |      | | Agent  | |
        # | | peer1  | |      | | peer2  | |        | | peer3  | |      | | peer4  | |
        # | +--------+ |      | +--------+ |        | +--------+ |      | +--------+ |
        # +------------+      +------------+        +------------+      +------------+
        # |Transit XDP |      |Transit XDP |        |Transit XDP |      |Transit XDP |
        # |    eth0    |      |    eth0    |        |    eth0    |      |    eth0    |
        # +------------+      +------------+        +------------+      +------------+
        #       |                   |                     |                   |
        #       |   +------------+  |                     |   +------------+  |
        #       |   |  Switch1   |  |                     |   |  Switch2   |  |
        #       |   |10.0.0.0/16 |  |                     |   |20.0.0.0/16 |  |
        #       |   |            |  |                     |   |            |  |
        #       |   |            |  |                     |   |            |  |
        #       |   |            |  |                     |   |            |  |
        #       +---|            |--+                     +---|            |--+
        #           |            |                            |            |
        #           |            |                            |            |
        #           +------------+                            +------------+
        #           |Transit XDP |                            |Transit XDP |
        #           |    eth0    |                            |    eth0    |
        #           +------------+                            +------------+
        #                  |              +------------+             |
        #                  |              |  Router1   |             |
        #                  |              |    VPC3    |             |
        #                  |              |            |             |
        #                  |              |            |             |
        #                  |              |            |             |
        #                  +--------------|            |-------------+
        #                                 |            |
        #                                 |            |
        #                                 +------------+
        #                                 |Transit XDP |
        #                                 |    eth0    |
        #                                 +------------+

        self.droplets = {
            "d1": droplet("d1"),
            "d2": droplet("d2"),
            "d3": droplet("d3"),
            "d4": droplet("d4"),
            "switch-1": droplet("switch-1"),
            "switch-2": droplet("switch-2"),
            "router-1": droplet("router-1")
        }

        c = controller(self.droplets)

        c.create_vpc(3, cidr("16", "10.0.0.0"), ["router-1"])
        c.create_network(3, 10, cidr("24", "10.0.0.0"), ["switch-1"])
        c.create_network(3, 20, cidr("24", "10.20.0.0"), ["switch-2"])

        self.ep1 = c.create_simple_endpoint(3, 10, "10.0.0.2", "d1")
        self.ep2 = c.create_simple_endpoint(3, 10, "10.0.0.3", "d2")

        self.ep3 = c.create_simple_endpoint(3, 20, "10.20.0.4", "d3")
        self.ep4 = c.create_simple_endpoint(3, 20, "10.20.0.5", "d4")

        # Delete an endpoint in subnet, delete the parent subnet, then parent VPC.
        self.ep3 = c.delete_simple_endpoint(3, 20, "10.20.0.4", "d3")
        c.delete_network(3, 20, cidr("24", "10.20.0.0"), ["switch-2"])
        c.delete_vpc(3, cidr("16", "10.0.0.0"), ["router-1"])

    def tearDown(self):
        pass

    def test_delete_one_at_a_time(self):
        logger.info(
            "{} Testing vpc properly deleted! {}".format('='*20, '='*20))
        do_validate_delete_test(self, list(self.droplets.values()))
        do_check_failed_rpcs(self, self.droplets.values())

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


class test_switch_local(unittest.TestCase):

    def setUp(self):
        # Testing the following basic scenario
        # +-------------------------+       +-------------------------+
        # |           left          |       |   right (and switch)    |
        # | +--------+   +--------+ |       | +--------+   +--------+ |
        # | |  ns0   |   |  ns2   | |       | |  ns1   |   |  ns3   | |
        # | |        |   |        | |       | |        |   |        | |
        # | +--------+   +--------+ |       | +--------+   +--------+ |
        # | | veth0  |   | veth0  | |       | | veth0  |   | veth0  | |
        # | |10.0.0.1|   |10.0.0.3| |       | |10.0.0.2|   |10.0.0.4| |
        # | +--------+   +--------+ |       | +--------+   +--------+ |
        # |      |            |     |       |      |            |     |
        # |      |            |     |       |      |            |     |
        # |      |            |     |       |      |            |     |
        # | +--------+   +--------+ |       | +--------+   +--------+ |
        # | |Transit |   |Transit | |       | |Transit |   |Transit | |
        # | | Agent  |   | Agent  | |       | | Agent  |   | Agent  | |
        # | | peer0  |   | peer2  | |       | | peer1  |   | peer3  | |
        # | +--------+   +--------+ |       | +--------+   +--------+ |
        # +-------------------------+       +-------------------------+
        # |       Transit XDP       |       |       Transit XDP       |
        # |          eth0           |       |  eth0 (Switch is here)  |
        # +-------------------------+       +-------------------------+

        self.droplets = {
            "left": droplet("left"),
            "right": droplet("right"),
        }
        c = controller(self.droplets)

        c.create_vpc(3, cidr("16", "10.0.0.0"), [])
        c.create_network(3, 1, cidr("16", "10.0.0.0"), ["right"])

        self.ep0 = c.create_simple_endpoint(3, 1, "10.0.0.2", "left")
        print("######## epip {}".format(self.ep0.ip))
        self.ep1 = c.create_simple_endpoint(3, 1, "10.0.0.4", "left")
        self.ep2 = c.create_simple_endpoint(3, 1, "10.0.0.3", "right")
        self.ep3 = c.create_simple_endpoint(3, 1, "10.0.0.5", "right")

    def tearDown(self):
        pass

    def test_switch_local(self):
        logger.info(
            "{} Testing Switch is on the host of destination endpoint! {}".format('='*20, '='*20))
        do_common_tests(self, self.ep0, self.ep2)

        logger.info("{} Testing both endpoints are local but switch is remote! {}".format(
            '='*20, '='*20))
        do_common_tests(self, self.ep0, self.ep1)

        logger.info("{} Testing both endpoints are on same host as switch! {}".format(
            '='*20, '='*20))
        do_common_tests(self, self.ep2, self.ep3)

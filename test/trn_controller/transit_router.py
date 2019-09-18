# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.common import logger


class transit_router:
    def __init__(self, droplet):
        self.droplet = droplet
        self.ip = self.droplet.ip
        self.id = droplet.id
        self.networks = {}

    def update_net(self, net):
        """
        Calls an update_net rpc to the transit router's droplet. After
        this the transit router has an updated list of the network's
        transit switch. Also calls update_substrate_endpoint to
        populate the mac addresses of the transit switches' droplets.
        """
        logger.info("[ROUTER {}]: update_net {}".format(self.id, net.netid))
        self.droplet.update_net(net)

        # Now update the mac address of the switches
        for s in net.transit_switches.values():
            self.droplet.update_substrate_ep(s.droplet)

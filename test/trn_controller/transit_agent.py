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


class transit_agent:
    def __init__(self, veth_peer, droplet):
        self.droplet = droplet
        self.veth_peer = veth_peer
        self.id = self.droplet.id
        self.transit_switches = {}

    def update_agent_metadata(self, ep, net):
        """
        Calls update_agent_metafata to update the agents with
        modifications in net transit switches or endpoint data.

        1. Update the list of transit switches of the endpoint's
           network (update_agent_metadata)
        2. Update the substrate endpoints with the switches mac/ip
           addresses. This is necessary since the data-plane do not do
           ARP actively if the mac is missing (at this point).
        """
        logger.info("[AGENT {}]: update_agent_metadata {}".format(
            self.id, net.netid))
        self.droplet.update_agent_metadata(self.veth_peer, ep, net)

        # Now update the transit switches mac
        self.transit_switches = net.transit_switches

        for s in self.transit_switches.values():
            self.droplet.update_agent_substrate_ep(self.veth_peer, s.droplet)

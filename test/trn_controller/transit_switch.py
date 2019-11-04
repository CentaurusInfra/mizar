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

from test.trn_controller.common import logger


class transit_switch:
    def __init__(self, droplet):
        self.droplet = droplet
        self.id = droplet.id
        self.ip = self.droplet.ip
        self.endpoints = {}
        self.transit_routers = {}
        self.known_routers = []

    def update_endpoint(self, ep):
        """
        Calls an update_endpoint rpc to transit switch's droplet.
        After this the switch can forward tunneled packets to the
        endpoint's host. Also calls update_substrate_ep to
        populate the mac addresses of the endpoint's host.
        """
        logger.info(
            "[SWITCH {}, {}]: update_endpoint {}".format(self.ip, self.id, ep.ip))

        self.droplet.update_ep(ep)
        # Now update the mac address of the endpoint's host
        if ep.host is not None:
            self.droplet.update_substrate_ep(ep.host)

    def update_vpc(self, vpc):
        """
        Calls an update_vpc rpc to the transit switch's droplet. After
        this the switch has an updated list of the VPC's transit
        routers. Also calls update_substrate_ep to populate the
        mac addresses of the transit routers' droplets.
        """
        logger.info("[SWITCH {}, {}]: update_vpc {}".format(
            self.ip, self.id, vpc.vni))
        self.droplet.update_vpc(vpc)

        # Now update the mac addresses of the routers' droplet
        self.transit_routers = vpc.transit_routers
        for r in self.transit_routers.values():
            if r not in self.known_routers:
                self.droplet.update_substrate_ep(r.droplet)
                self.known_routers.append(r)

    def delete_vpc(self, vpc):
        """
        Calls a delete_vpc rpc on the transit switch's droplet.
        Also calls delete_substrate_ep to remove the
        mac addresses of the transit routers' droplets.
        """
        logger.info("[SWITCH {}, {}]: update_vpc {}".format(
            self.ip, self.id, vpc.vni))

        # Now delete the mac addresses of the routers' droplet
        for r in self.transit_routers.values():
            self.droplet.delete_substrate_ep(r.droplet)

        self.droplet.delete_vpc(vpc)

    def delete_endpoint(self, ep):
        """
        Calls a delete_endpoint rpc to transit switch's droplet.
        Also calls delete_substrate_ep to
        remove the mac addresses of the endpoint's host.
        """
        logger.info(
            "[SWITCH {}, {}]: delete_endpoint {}".format(self.ip, self.id, ep.ip))

        self.droplet.delete_ep(ep)

        # Now remove the mac address of the endpoint's host
        if ep.host is not None:
            self.droplet.delete_substrate_ep(ep.host)

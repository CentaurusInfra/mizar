# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.network import network
from test.trn_controller.transit_router import transit_router
from test.trn_controller.common import cidr, logger


class vpc:
    def __init__(self, vni, cidr):
        """
        A VNI is a 64 bit integer. Basically the most signifigant 32-bits encode
        a tenant ID and the least significant 32-bits encode a vpc
        that belongs to the that tenant.

        Each vpc has a set of transit routers that rewrites packets
        between the transit switches of networks within the VPC. A
        transit router has no information about endpoint's host but
        only about the transit switches of the endpoint's network.

        - routers: is a dictionary of all droplets hosting a transit
          router of the VPC
        - networks: is a dictionary of all networks within the VPC.
        """
        self.vni = vni
        self.cidr = cidr
        self.transit_routers = {}
        self.networks = {}

    def get_tunnel_id(self):
        return str(self.vni)

    def get_transit_routers_ips(self):
        return [str(r.ip) for r in self.transit_routers.values()]

    def add_router(self, droplet):
        """
        Add a new transit router hosted at droplet to the set transit
        routers.

        1. Adds the router to the set of transit routers
        2. Call update_net on the transit router's droplet for each
           network of the VPC. These calls populate the transit
           routers table with the set of transit switches of each
           network.
        3. Call update_vpc on each network of the VPC. This call allows
           all transit switches of all networks to learn about the new
           router and starts sending packets to it. Thus, must be
           called after all transit router's data has been populated.
        """

        logger.info("[VPC {}]: add_router {}".format(self.vni, droplet.id))

        id = droplet.id
        self.transit_routers[id] = transit_router(droplet)

        for net in self.networks.values():
            self.transit_routers[id].update_net(net)
            net.update_vpc(self)

    def create_network(self, netid, cidr):
        """
        Creates a network in the VPC. Since the network does not have
        transit switches yet, this function just adds a network object
        to the set of networks.
        """
        logger.info("[VPC {}]: create_network {}".format(self.vni, netid))
        self.networks[netid] = network(self.vni, netid, cidr)
        self.networks[netid].create_gw_endpoint()

    def add_switch(self, netid, droplet):
        """
        Adds a switch to the network identified by netid.

        1. Cascade the add switch call to the network, which populate
           the data of the new transit switch including the set of
           transit routers of the VPC.
        2. Call update_net on all the VPC's transit routers to allow
           the routers to forward traffic to the new switch. From
           traffic perspective, the order of update_net and add_switch
           is not important in this case. We just need to call
           update_net here after the switch is added to the transit
           switches set of the network.
        """

        logger.info("[VPC {}]: add_switch {}".format(self.vni, droplet.id))
        self.networks[netid].add_switch(self, droplet)

        for r in self.transit_routers.values():
            r.update_net(self.networks[netid])

    def create_simple_endpoint(self, netid, ip, host):
        """
        Creates a new simple endpoint in a network within the vpc.
        Since the routers need not to be updated with the endpoint
        data, this call is just cascaded to the network.
        """
        logger.info(
            "[VPC {}]: create_simple_endpoint {}".format(self.vni, ip))
        return self.networks[netid].create_simple_endpoint(ip, host)

    def create_vxlan_endpoint(self, netid, ip, host):
        """
        Creates a vxlan port on the host for backward compatability tests.
        """
        logger.info(
            "[VPC {}]: create_vxlan_endpoint {}".format(self.vni, ip))
        return self.networks[netid].create_vxlan_endpoint(ip, host)

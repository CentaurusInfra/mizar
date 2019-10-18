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

from test.trn_controller.vpc import vpc
from test.trn_controller.network import network
from test.trn_controller.endpoint import endpoint
from test.trn_controller.droplet import droplet
from test.trn_controller.common import cidr, logger


class controller:
    def __init__(self, droplets):
        """
        A controller needs to be aware of the hosts (droplets).
        Pass this during initialization. The controller functions are
        always cascaded from higher level resources to lower level
        resources.

        For example to create an endpoint, the controller calls
        create_endpoint function on the vpc of the endpoint, then the
        vpc resource calls create_endpoint on the network resources,
        then the network resource is actually realizing the endpoint.

        This approach allows the controller to properly propagate
        information accorss transit XDP programs and transit agents.

        - vpcs: is a dictionary of all vpcs mananged by the
          controllers (key: vni)
        - droplets: a dictionary of all droplets managed by controller
          (key: droplet id). In a production controller this is a list
          of all hosts.
        """
        self.vpcs = {}
        self.droplets = droplets

    def create_vpc(self, vni, cidr, routers):
        """
        Create a vpc of unique VNI, CIDR block and optional list of
        routers.
        1. Adds the vpc to the VPCs dict
        2. For that VPC, call add_router for each router in the list
        """

        logger.info("[Controller]: create_vpc {}".format(vni))
        self.vpcs[vni] = vpc(vni, cidr)
        for r in routers:
            self.add_router(vni, r)

    def create_network(self, vni, netid, cidr, switches):
        """
        Creates a network in a VPC identified by VNI.
        1. Call create_network in that VPC
        2. For that network, call add_switch for each switch in the list
        """
        logger.info("[Controller]: create_network {}.{}".format(vni, netid))
        self.vpcs[vni].create_network(netid, cidr)
        for s in switches:
            self.add_switch(vni, netid, s)

    def create_simple_endpoint(self, vni, netid, ip, host):
        """
        Adds a simple endpoint to an existing network
        """
        logger.info(
            "[Controller]: create_simple_endpoint {}.{}.{}".format(vni, netid, ip))
        return self.vpcs[vni].create_simple_endpoint(netid, ip, self.droplets[host])

    def delete_simple_endpoint(self, vni, netid, ip, host):
        """
        Deletes a simple endpoint from an existing network
        """
        logger.info(
            "[Controller]: delete_simple_endpoint {}.{}.{}".format(vni, netid, ip))
        return self.vpcs[vni].delete_simple_endpoint(netid, ip, self.droplets[host])

    def delete_network(self, vni, netid, cidr, switches):
        """
        Deletes a network in a VPC identified by VNI.
        1. Call delete_network on that VPC
        """
        logger.info("[Controller]: delete_network {}.{}".format(vni, netid))
        self.vpcs[vni].delete_network(netid, cidr)

    def delete_vpc(self, vni, cidr, routers):
        """
        Deletes the vpc with the unique VNI, CIDR block and optional list of
        routers.
        1. Removes the vpc from the VPCs dict
        2. Call delete_network on all networks in the VPC
        3. For that VPC, call remove_router for each router in the list
        """

        logger.info("[Controller]: remove_vpc {}".format(vni))
        vpc = self.vpcs.pop(vni)
        for net in list(vpc.networks.values()):
            vpc.delete_network(net.netid, net.cidr)
        for r in routers:
            self.remove_router(vni, r, vpc)

    def create_vxlan_endpoint(self, vni, netid, ip, host):
        """
        Adds a vxlan endpoint to an existing network for backward
        compatibility tests.
        """
        logger.info(
            "[Controller]: create_vxlan_endpoint {}.{}.{}".format(vni, netid, ip))
        return self.vpcs[vni].create_vxlan_endpoint(netid, ip, self.droplets[host])

    def add_router(self, vni, r):
        """
        Adds a new router to an existing VPC.
        """
        router = self.droplets[r]
        logger.info(
            "[Controller]: add_router {} to vpc {}".format(router.id, vni))
        self.vpcs[vni].add_router(router)

    def add_switch(self, vni, netid, s):
        """
        Adds a new switch to an existing network.
        """
        switch = self.droplets[s]
        logger.info(
            "[Controller]: add_switch {} to network {}.{}".format(switch.id, vni, netid))
        self.vpcs[vni].add_switch(netid, switch)

    def remove_switch(self, vni, netid, s, net=None):
        """
        Removes a switch from an existing network
        """
        if net is None:
            net = self.vpcs[vni].networks[netid]
        switch = self.droplets[s]
        logger.info(
            "[Controller]: remove_switch {} from network {}.{}".format(switch.id, vni, netid))
        self.vpcs[vni].remove_switch(netid, switch, net)

    def remove_router(self, vni, r, vpc=None):
        """
        Removes an existing router from an existing VPC.
        """
        if vpc is None:
            vpc = self.vpcs[vni]
        router = self.droplets[r]
        logger.info(
            "[Controller]: remove_router {} from vpc {}".format(router.id, vni))
        vpc.remove_router(router)

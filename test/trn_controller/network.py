# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.endpoint import endpoint
from test.trn_controller.transit_router import transit_router
from test.trn_controller.transit_switch import transit_switch
from test.trn_controller.common import cidr, logger
import time


class network:
    def __init__(self, vni, netid, cidr):
        """
        A network is identified by a netid. Each network has a set of
        transit switches that rewrite tunneled packets to route them
        between endpoints hosted in the network.

        - cidr: the network cidr block
        - switches: a dictionary of all droplets running a transit
          switch of this network
        - endpoints: a dictionary of all endpoints within the network
        """
        self.vni = vni
        self.netid = netid
        self.cidr = cidr
        self.transit_switches = {}
        self.endpoints = {}

    def get_gw_ip(self):
        return self.cidr.get_ip(1)

    def get_ovs_bridge_name(self):
        return 'br_' + self.get_tunnel_id()

    def get_tunnel_id(self):
        return str(self.vni)

    def get_nip(self):
        return str(self.cidr.ip)

    def get_prefixlen(self):
        return str(self.cidr.prefixlen)

    def get_switches_ips(self):
        return [str(s.ip) for s in self.transit_switches.values()]

    def update_vpc(self, vpc):
        """
        Called when vpc data changes (e.g router is added to the VPC).
        Cascades an update_vpc rpc to all transit switches of the network.
        """
        logger.info("[NETWORK {}]: update_vpc {}".format(
            self.netid, vpc.vni))

        for switch in self.transit_switches.values():
            switch.update_vpc(vpc)

    def add_switch(self, vpc, droplet):
        """
        Adds a transit switch of this network hosted at the given droplet.
        1. Creates the switch object and add it to the list
        2. Call update_vpc on the new transit switch's droplet to
           update it with the list of transit routers of the VPC
        3. Call update_endpoint on the transit switch's droplet to
           update it with all endpoint's data within this network
        4. Finally call update on each endpoint's
           transit agent within the network, so they can start sending
           packets to the new transit switch.
        """
        logger.info("[NETWORK {}]: add_switch {}".format(
            self.netid, droplet.id))
        id = droplet.id
        self.transit_switches[id] = transit_switch(droplet)
        self.transit_switches[id].update_vpc(vpc)

        for ep in self.endpoints.values():
            self.transit_switches[id].update_endpoint(ep)

        for ep in self.endpoints.values():
            ep.update(self)

    def create_gw_endpoint(self):
        """
        Allocates the first IP of the network CIDR range and
        Creates a phantom endpoint (without a host).
        """
        ip = self.get_gw_ip()

        if ip in self.endpoints:
            raise ValueError("Endpoint IP {} is already in use.".format(ip))

        logger.info("[NETWORK {}]: create_gw_endpoint {}".format(
            self.netid, ip))

        self.endpoints[ip] = endpoint(self.vni, self.netid, ip=ip, prefixlen=self.cidr.prefixlen, gw_ip=None, host=None)

        # Now update the endpoint on the remaining switches
        for switch in self.transit_switches.values():
            switch.update_endpoint(self.endpoints[ip])

        return self.endpoints[ip]


    def create_simple_endpoint(self, ip, host):
        """
        Creates a simple endpoint in the network.
        1. First create the endpoint object and add it to the set of
           endpoints
        2. Call update_endpoint on at least one transit switch of the
           network (two or three switches may be a good idea in production!).
        3. Call update on each endpoint's transit agent within the
           network. The endpoint becomes ready to send  packets.
        """
        logger.info("[NETWORK {}]: create_simple_endpoint {}".format(
            self.netid, ip))

        if ip in self.endpoints:
            raise ValueError("Endpoint IP {} is already in use.".format(ip))

        switches = list(self.transit_switches.values())

        # Create a temp network object of only one switch
        temp_net = network(self.vni, self.netid, self.cidr)
        temp_net.transit_switches[switches[0].id] = switches[0]

        start = time.time()

        self.endpoints[ip] = endpoint(self.vni, self.netid, ip=ip, prefixlen=self.cidr.prefixlen, gw_ip=self.get_gw_ip(), host=host)

        switches[0].update_endpoint(self.endpoints[ip])
        self.endpoints[ip].update(temp_net)

        end = time.time()
        ep_ready_time = end-start
        logger.info("[NETWORK {}]: endpoint {} provisioned and ready in {:5.4f} seconds (O(1)!).".format(
            self.netid, ip, ep_ready_time))

        # Now update the endpoint on the remaining switches
        for switch in switches[1:]:
            switch.update_endpoint(self.endpoints[ip])

        # Update the endpoint again with the full switches
        self.endpoints[ip].update(self)

        return self.endpoints[ip]

    def create_vxlan_endpoint(self, ip, host):
        """
        Creates a vxlan endpoint
        """
        logger.info("[NETWORK {}]: create_vxlan_endpoint {}".format(
            self.netid, ip))
        br = self.get_ovs_bridge_name()
        if (not host.ovs_is_exist(br)):
            host.ovs_add_bridge(br)
        self.endpoints[ip] = endpoint(
            self.vni, self.netid, ip=ip, prefixlen=self.cidr.prefixlen, gw_ip=self.get_gw_ip(),host=host, tuntype='vxn', bridge=br)

        # Create a geneve tunnel interface to one of the switches
        transit_itf = 'vxn_transit'
        switch = list(self.transit_switches.values())[0]
        transit_port = host.ovs_create_geneve_tun_itf(
            br, transit_itf, self.vni, switch.ip)
        host.ovs_add_transit_flow(
            br, self.endpoints[ip].bridge_port, transit_port)

        # We now tell the transit switch about the endpoint
        for s in self.transit_switches.values():
            s.update_endpoint(self.endpoints[ip])

        # Create vxlan tunnel interface to all vxlan endpoints
        for ep_i in self.endpoints.values():
            if ep_i.host is None or ep_i.tuntype != 'vxn':
                continue

            for ep_j in self.endpoints.values():
                if ep_j.host is None:
                    continue

                if ep_i.host.ip == ep_j.host.ip:
                    continue

                if ep_j.tuntype == 'vxn':
                    remote_ip = ep_j.host.ip
                    out_port = ep_i.host.ovs_create_vxlan_tun_itf(
                        br, ep_j.tunitf, self.vni, remote_ip)
                    ep_i.host.add_vxlan_ofrule(
                        br, ep_i.bridge_port, out_port, ep_j.ip)

        return self.endpoints[ip]

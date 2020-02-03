# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>
#          Haibin Michael Xie
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.common import cidr, logger, veth_allocator, CONSTANTS
from test.trn_controller.transit_agent import transit_agent
from time import sleep


class endpoint:
    """
    An endpoint of IP address in vni and hosted on host. The endpoint
    can use a tunnel type tuntype: gnv (geneve) or vxn (vxlan).
    Default is gnv.
    WARNING: The vxlan type is created for a _limited_ backward compatability
    tests. It does not support test scenarios require for e.g.:
    multiple vxlan tunnel keys, subneting, ... etc.
    """

    def __init__(self, vni, netid, ip, vpc_cidr, net_cidr, gw_ip, host, tuntype='gnv', bridge='br0', host_ep=False, eptype=CONSTANTS.TRAN_SIMPLE_EP, backends=None,
                 scaled_ep_obj='/trn_xdp/trn_transit_scaled_endpoint_ebpf_debug.o'):
        """
        Defines a simple endpoint in the VPC and network. Also defines
        a phantom endpoint that is not hosted on any host (switch only respond for ARP requests).

        1. Calls provision_simple_endpoint on the droplet to create a
           veth pair and load the transit agent xdp program
        2. Calls update_ep on endpoint's host.
        """
        self.vni = vni
        self.netid = netid
        v = veth_allocator.getInstance().allocate_veth()
        self.veth_name = "veth0"
        self.mac = v[0]
        self.ns = tuntype + '_' + v[1]
        self.veth_peer = tuntype + '_' + v[2]
        self.veth_allocated = True
        self.ip = ip
        self.prefixlen = net_cidr.prefixlen
        self.netip = net_cidr.ip
        self.vpc_cidr = vpc_cidr
        self.gw_ip = gw_ip
        self.eptype = eptype
        self.host = host
        self.transit_agent = None
        self.tuntype = tuntype
        self.tunitf = 'tun_' + self.veth_peer  # Only for ovs
        self.bridge = bridge
        self.bridge_port = None
        self.host_ep = host_ep
        self.ns_exec = f'''ip netns exec {self.ns} '''
        if host_ep:
            self.veth_name = "host_" + self.veth_name
            self.veth_peer = "host_" + self.veth_peer
            self.ns = ""
            self.ns_exec = ""
        self.backends = backends
        self.scaled_ep_obj = scaled_ep_obj

        self.provision()

        # endpoint commands
        self.output_dir = '/mnt/Transit/test/trn_func_tests/output'
        self.tcp_recv_file = f'''{self.output_dir}/{self.ns}_{self.ip}_tcp_recv'''
        self.tcp_sent_file = f'''{self.output_dir}/{self.ns}_{self.ip}_tcp_sent'''

        self.udp_recv_file = f'''{self.output_dir}/{self.ns}_{self.ip}_udp_recv'''
        self.udp_sent_file = f'''{self.output_dir}/{self.ns}_{self.ip}_udp_sent'''

        self.ping_cmd = f'''{self.ns_exec}ping'''
        self.curl_cmd = f'''{self.ns_exec}curl'''
        self.python_cmd = f'''{self.ns_exec}python3'''
        self.diff_cmd = f'''{self.ns_exec}diff'''
        self.bash_cmd = f'''{self.ns_exec}bash -c'''
        self.httpd_cmd = f'''{self.bash_cmd} 'pushd /tmp/{self.ns}_{self.ip}; python3 -m http.server > /tmp/{self.ns}_{self.ip}/httpd.log 2>&1' '''
        self.tcp_server_cmd = f'''{self.bash_cmd} '(nc -l -p 9001 > {self.tcp_recv_file})' '''
        self.udp_server_cmd = f'''{self.bash_cmd} '(nc -u -l -p 5001 > {self.udp_recv_file})' '''
        self.iperf3_server_cmd = f'''{self.bash_cmd} 'iperf3 -s > /tmp/{self.ns}_{self.ip}/iperf_server.log 2>&1' '''

        self.tcp_serv_idle_cmd = f'''{self.bash_cmd} './mnt/Transit/tools/tcp_server.py' '''
        self.tcp_client_idle_cmd = f'''{self.bash_cmd} './mnt/Transit/tools/tcp_client.py '''

    def provision(self):
        if self.host is None or self.eptype is not CONSTANTS.TRAN_SIMPLE_EP:
            return

        if self.tuntype == 'vxn':
            self.bridge_port = self.host.provision_vxlan_endpoint(self)
        elif self.host_ep:
            self.transit_agent = transit_agent(self.veth_peer, self.host)
            self.host.provision_host_endpoint(self)
        else:
            self.transit_agent = transit_agent(self.veth_peer, self.host)
            self.host.provision_simple_endpoint(self)

        # Since we are in compatability mode, we need to also tell the
        # transit XDP about the endpoint even if it is a vxlan
        self.host.update_ep(self)
        self.ready = False

    def unprovision(self):
        if self.host is None:
            return

        if self.tuntype == 'vxn':
            return
        else:
            self.transit_agent = None
            self.host.delete_ep(self)
            self.host.unprovision_simple_endpoint(self)
            veth_allocator.getInstance().reclaim_veth(
                self.mac, self.ns.replace(self.tuntype + '_', ''), self.veth_peer.replace(self.tuntype + '_', ''))
            self.veth_allocated = False

        self.ready = False

    def __del__(self):
        if (self.tuntype == 'gnv' and self.host):
            if self.transit_agent is not None:
                self.host.unload_transit_agent_xdp(self.veth_peer)
            if self.veth_allocated:
                veth_allocator.getInstance().reclaim_veth(
                    self.mac, self.ns.replace(self.tuntype + '_', ''), self.veth_peer.replace(self.tuntype + '_', ''))

    def get_tunnel_id(self):
        return str(self.vni)

    def get_ip(self):
        return str(self.ip)

    def get_eptype(self):
        return str(self.eptype)

    def get_mac(self):
        return str(self.mac)

    def get_veth_peer(self):
        return self.veth_peer

    def get_veth_name(self):
        return self.veth_name

    def get_remote_ips(self):
        remote_ips = []
        if self.eptype is CONSTANTS.TRAN_SCALED_EP:
            remote_ips = self.backends and [str(be.ip) for be in self.backends]
        else:
            remote_ips = self.host and [str(self.host.ip)]

        return remote_ips

    def update(self, net):
        """
        Prepares or update the endpoint to send traffic. An endpoint
        is assumed ready to serve traffic if this function is called once.
        """
        logger.info(
            "[EP {}]: prepare endpoint".format(self.ip))
        if self.host is not None and self.eptype is CONSTANTS.TRAN_SIMPLE_EP:
            self.transit_agent.update_agent_metadata(self, net)
        self.ready = True

    def delete(self, net):
        """
        Deletes the endpoint information.
        We do not need to delete the agent metadate or agent substrate.
        Unloading the agent will clear this information.
        """
        logger.info(
            "[EP {}]: delete endpoint".format(self.ip))
        self.unprovision()

    def do_ping(self, ip, count=1, wait=5):
        cmd = f'''{self.ping_cmd} -w {wait} -c {count} {ip}'''
        return self.host.run(cmd)

    def do_curl(self, args):
        cmd = f'''{self.curl_cmd} {args}'''
        return self.host.run(cmd)

    def do_httpd(self):
        self.host.run(self.httpd_cmd, detach=True)
        sleep(1)

    def do_tcp_serve(self):
        return self.host.run(self.tcp_server_cmd, detach=True)

    def do_udp_serve(self):
        return self.host.run(self.udp_server_cmd, detach=True)

    def do_long_tcp_client(self, ip):
        count = 10
        interval = 1
        self.do_tcp_client(ip, bs=100, count=count,
                           interval=interval, detach=True)
        check_after = count * interval + 2
        return check_after

    def do_long_udp_client(self, ip):
        count = 10
        interval = 1
        self.do_udp_client(ip, bs=100, count=count,
                           interval=interval, detach=True)
        check_after = count * interval + 2
        return check_after

    def do_tcp_client(self, ip, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        dd_cmd = f'''dd if=/dev/urandom  bs={bs} count={count} | tee {self.tcp_sent_file}'''
        cmd = f'''{self.bash_cmd} '({dd_cmd} | nc {ip} 9001 {delay} -w1)' '''
        return self.host.run(cmd, detach)

    def do_udp_client(self, ip, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        dd_cmd = f'''dd if=/dev/urandom  bs={bs} count={count} | tee {self.udp_sent_file}'''
        cmd = f'''{self.bash_cmd} '({dd_cmd} | nc -u {ip} 5001 {delay} -w1)' '''
        return self.host.run(cmd, detach)

    def do_diff_tcp(self, client_ep, server_ep):
        cmd = f'''{self.diff_cmd} {server_ep.tcp_recv_file} {client_ep.tcp_sent_file}'''
        return self.host.run(cmd)

    def do_diff_udp(self, client_ep, server_ep):
        cmd = f'''{self.diff_cmd} {server_ep.udp_recv_file} {client_ep.udp_sent_file}'''
        return self.host.run(cmd)

    def do_iperf3_server(self):
        self.host.run(self.iperf3_server_cmd, detach=True)
        # wait for server to start
        sleep(1)

    def do_iperf3_client(self, ip, args=''):
        cmd = f'''{self.bash_cmd} 'iperf3 -c {ip} {args}' '''
        return self.host.run(cmd)

    def do_tcp_serve_idle(self, detach=True):
        return self.host.run(self.tcp_serv_idle_cmd, detach=detach)

    def do_tcp_client_idle(self, ip, message_count=2, delay=5, detach=True):
        return self.host.run(self.tcp_client_idle_cmd + str(ip) + " " + str(message_count) + " " + str(delay) + "'", detach=detach)

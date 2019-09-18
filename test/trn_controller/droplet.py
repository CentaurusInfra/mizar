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
from test.trn_controller.common import cidr, logger, run_cmd
import os
import docker
from time import sleep
import json


class droplet:
    def __init__(self, id, droplet_type='docker'):
        """
        Models a host that runs the transit XDP program. In the
        functional test this is simply a docker container.
        """
        self.id = id
        self.droplet_type = droplet_type
        self.container = None
        self.ip = None
        self.mac = None
        self.veth_peers = set()

        # transitd cli commands
        self.trn_cli = f'''/trn_bin/transit'''
        self.trn_cli_load_transit_xdp = f'''{self.trn_cli} load-transit-xdp -i eth0 -j'''
        self.trn_cli_unload_transit_xdp = f'''{self.trn_cli} unload-transit-xdp -i eth0 -j'''
        self.trn_cli_update_vpc = f'''{self.trn_cli} update-vpc -i eth0 -j'''
        self.trn_cli_get_vpc = f'''{self.trn_cli} get-vpc -i eth0 -j'''
        self.trn_cli_update_net = f'''{self.trn_cli} update-net -i eth0 -j'''
        self.trn_cli_get_net = f'''{self.trn_cli} get-net -i eth0 -j'''
        self.trn_cli_update_ep = f'''{self.trn_cli} update-ep -i eth0 -j'''
        self.trn_cli_get_ep = f'''{self.trn_cli} get-ep -i eth0 -j'''

        self.trn_cli_load_transit_agent_xdp = f'''{self.trn_cli} load-agent-xdp'''
        self.trn_cli_unload_transit_agent_xdp = f'''{self.trn_cli} unload-agent-xdp'''
        self.trn_cli_update_agent_metadata = f'''{self.trn_cli} update-agent-metadata'''
        self.trn_cli_get_agent_metadata = f'''{self.trn_cli} get-agent-metadata'''
        self.trn_cli_update_agent_ep = f'''{self.trn_cli} update-agent-ep'''
        self.trn_cli_get_agent_ep = f'''{self.trn_cli} get-agent-ep'''

        self.xdp_path = "/trn_xdp/trn_transit_xdp_ebpf_debug.o"
        self.pcap_file = "/bpffs/transit_xdp.pcap"

        self.agent_xdp_path = "/trn_xdp/trn_agent_xdp_ebpf_debug.o"
        self.agent_pcap_file = "/bpffs/agent_xdp.pcap"
        self.main_bridge = 'br0'
        self.bootstrap()

    def bootstrap(self):
        if self.droplet_type == 'docker':
            self._create_docker_container()
            self.load_transit_xdp()
            self.start_pcap()
            return

        logger.error("Unsupported droplet type!")

    def provision_simple_endpoint(self, ep):
        """
        Creates a veth pair and a namespace for the endpoint and loads
        the transit agent program on the veth peer running in the root
        namespace.
        """
        logger.info(
            "[DROPLET {}]: provision_simple_endpoint {}".format(self.id, ep.ip))

        self._create_veth_pair(ep)
        self.load_transit_agent_xdp(ep.veth_peer)

    def provision_vxlan_endpoint(self, ep):
        logger.info(
            "[DROPLET {}]: provision_vxlan_endpoint {}".format(self.id, ep.ip))
        self._create_veth_pair(ep)
        return self.ovs_add_port(ep.bridge, ep.veth_peer)

    def _create_veth_pair(self, ep):
        """
        Creates a veth pair. br0 must have been created.
        """
        logger.info(
            "[DROPLET {}]: _create_veth_pair {}".format(self.id, ep.ip))

        script = (f''' bash -c '\
mkdir -p /tmp/{ep.ns}_{ep.ip} && \
echo {ep.ip} > /tmp/{ep.ns}_{ep.ip}/index.html && \
ip netns add {ep.ns} && \
ip link add veth0 type veth peer name {ep.veth_peer} && \
ip link set veth0 netns {ep.ns} && \
ip netns exec {ep.ns} ip addr add {ep.ip}/{ep.prefixlen} dev veth0 && \
ip netns exec {ep.ns} ip link set dev veth0 up && \
ip netns exec {ep.ns} sysctl -w net.ipv4.tcp_mtu_probing=2 && \
ip netns exec {ep.ns} ethtool -K veth0 tso off gso off ufo off && \
ip netns exec {ep.ns} ethtool --offload veth0 rx off tx off && \
ip link set dev {ep.veth_peer} up mtu 9000 && \
ip netns exec {ep.ns} route add default gw {ep.gw_ip} &&  \
ip netns exec {ep.ns} ifconfig lo up &&  \
ip netns exec {ep.ns} ifconfig veth0 hw ether {ep.mac} ' ''')

        self.run(script)
        self.veth_peers.add(ep.veth_peer)

    def load_transit_xdp(self):
        logger.info(
            "[DROPLET {}]: load_transit_xdp {}".format(self.id, self.ip))
        jsonconf = {
            "xdp_path": self.xdp_path,
            "pcapfile": self.pcap_file
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_load_transit_xdp} \'{jsonconf}\' '''
        self.run(cmd)

    def unload_transit_xdp(self):
        logger.info(
            "[DROPLET {}]: unload_transit_xdp {}".format(self.id, self.ip))
        jsonconf = '\'{}\''
        cmd = f'''{self.trn_cli_unload_transit_xdp} {jsonconf} '''
        self.run(cmd)

    def load_transit_agent_xdp(self, itf):
        logger.info(
            "[DROPLET {}]: load_transit_agent_xdp {}".format(self.id, itf))
        jsonconf = {
            "xdp_path": self.agent_xdp_path,
            "pcapfile": self.agent_pcap_file
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_load_transit_agent_xdp} -i \'{itf}\' -j \'{jsonconf}\' '''
        self.run(cmd)

    def unload_transit_agent_xdp(self, itf):
        logger.info(
            "[DROPLET {}]: unload_transit_agent_xdp {}".format(self.id, itf))
        jsonconf = '\'{}\''
        cmd = f'''{self.trn_cli_unload_transit_agent_xdp} -i \'{itf}\' -j {jsonconf} '''
        self.run(cmd)

    def update_vpc(self, vpc):
        logger.info(
            "[DROPLET {}]: update_vpc {}".format(self.id, vpc.get_tunnel_id()))

        jsonconf = {
            "tunnel_id": vpc.get_tunnel_id(),
            "routers_ips": vpc.get_transit_routers_ips()
        }

        jsonconf = json.dumps(jsonconf)

        cmd = f'''{self.trn_cli_update_vpc} \'{jsonconf}\''''
        self.run(cmd)

    def get_vpc(self, vpc):
        logger.info(
            "[DROPLET {}]: get_vpc {}".format(self.id, vpc.get_tunnel_id()))

        jsonconf = {
            "tunnel_id": vpc.get_tunnel_id(),
        }

        jsonconf = json.dumps(jsonconf)

        cmd = f'''{self.trn_cli_get_vpc} \'{jsonconf}\''''
        output = self.run(cmd)
        logger.info(output[0])
        logger.info(output[1])

    def update_net(self, net):
        logger.info(
            "[DROPLET {}]: update_net {}".format(self.id, net.netid))

        jsonconf = {
            "tunnel_id": net.get_tunnel_id(),
            "nip": net.get_nip(),
            "prefixlen": net.get_prefixlen(),
            "switches_ips": net.get_switches_ips()
        }

        jsonconf = json.dumps(jsonconf)

        cmd = f'''{self.trn_cli_update_net} \'{jsonconf}\''''
        self.run(cmd)

    def get_net(self, net):
        logger.info(
            "[DROPLET {}]: get_net {}".format(self.id, net.netid))

        jsonconf = {
            "tunnel_id": net.get_tunnel_id(),
            "nip": net.get_nip(),
            "prefixlen": net.get_prefixlen(),
        }

        jsonconf = json.dumps(jsonconf)

        cmd = f'''{self.trn_cli_get_net} \'{jsonconf}\''''
        output = self.run(cmd)
        logger.info(output[0])
        logger.info(output[1])

    def update_ep(self, ep):
        if ep.host is not None:
            logger.info(
                "[DROPLET {}]: update_ep {} hosted at {}".format(self.id, ep.ip, ep.host.id))
        else:
            logger.info(
                "[DROPLET {}]: update_ep for a phantom ep {}".format(self.id, ep.ip))

        peer = ""

        # Only detail veth info if the droplet is also a host
        if (ep.host and self.ip == ep.host.ip):
            peer = ep.get_veth_peer()

        jsonconf = {
            "tunnel_id": ep.get_tunnel_id(),
            "ip": ep.get_ip(),
            "eptype": ep.get_eptype(),
            "mac": ep.get_mac(),
            "veth": ep.get_veth_name(),
            "remote_ips": ep.get_remote_ips(),
            "hosted_iface": peer
        }

        jsonconf = json.dumps(jsonconf)

        cmd = f'''{self.trn_cli_update_ep} \'{jsonconf}\''''
        self.run(cmd)

    def get_ep(self, ep, agent=False):
        jsonconf = {
            "tunnel_id": ep.get_tunnel_id(),
            "ip": ep.get_ip(),
        }
        jsonconf = json.dumps(jsonconf)

        if agent:
            logger.info(
                "[DROPLET {}]: get_agent_ep {} hosted at {}".format(self.id, ep.ip, ep.host.id))
            cmd = f'''{self.trn_cli_get_agent_ep} \'{jsonconf}\''''
        else:
            logger.info(
                "[DROPLET {}]: get_ep {} hosted at {}".format(self.id, ep.ip, ep.host.id))
            cmd = f'''{self.trn_cli_get_ep} \'{jsonconf}\''''

        output = self.run(cmd)
        logger.info(output[0])
        logger.info(output[1])

    def get_agent_ep(self, ep):
        self.get_ep(ep, agent=True)

    def update_substrate_ep(self, droplet):
        logger.info(
            "[DROPLET {}]: update_substrate_ep for droplet {}".format(self.id, droplet.ip))

        jsonconf = droplet.get_substrate_ep_json()

        cmd = f'''{self.trn_cli_update_ep} \'{jsonconf}\''''
        self.run(cmd)

        jsonconf = {
            "tunnel_id": "0",
            "ip": droplet.ip,
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_get_ep} \'{jsonconf}\''''
        output = self.run(cmd)
        logger.info(output[0])
        logger.info(output[1])

    def update_agent_ep(self, itf):
        logger.error(
            "[DROPLET {}]: not implemented, no use case for now!".format(self.id))

    def update_agent_metadata(self, itf, ep, net):
        logger.info(
            "[DROPLET {}]: update_agent_metadata on {} for endpoint {}".format(self.id, itf, ep.ip))

        jsonconf = {
            "ep": {
                "tunnel_id": ep.get_tunnel_id(),
                "ip": ep.get_ip(),
                "eptype": ep.get_eptype(),
                "mac": ep.get_mac(),
                "veth": ep.get_veth_name(),
                "remote_ips": ep.get_remote_ips(),
                "hosted_iface": "eth0"
            },
            "net": {
                "tunnel_id": net.get_tunnel_id(),
                "nip": net.get_nip(),
                "prefixlen": net.get_prefixlen(),
                "switches_ips": net.get_switches_ips()
            },
            "eth": {
                "ip": self.ip,
                "mac": self.mac,
                "iface": "eth0"
            }
        }
        jsonconf = json.dumps(jsonconf)

        cmd = f'''{self.trn_cli_update_agent_metadata} -i \'{itf}\' -j \'{jsonconf}\''''
        self.run(cmd)

    def get_agent_metadata(self, itf, ep, net):
        logger.info(
            "[DROPLET {}]: get_agent_metadata on {} for endpoint {}".format(self.id, itf, ep.ip))

        jsonconf = {
            "": "",
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_get_agent_metadata} -i \'{itf}\' -j \'{jsonconf}\''''
        output = self.run(cmd)
        logger.info(output[0])
        logger.info(output[1])

    def update_agent_substrate_ep(self, itf, droplet):
        logger.info(
            "[DROPLET {}]: update_agent_substrate_ep on {} for droplet {}".format(self.id, itf, droplet.ip))

        jsonconf = droplet.get_substrate_ep_json()

        cmd = f'''{self.trn_cli_update_agent_ep} -i \'{itf}\' -j \'{jsonconf}\''''
        self.run(cmd)

        jsonconf = {
            "tunnel_id": "0",
            "ip": droplet.ip,
        }
        jsonconf = json.dumps(jsonconf)
        cmd = f'''{self.trn_cli_get_agent_ep} -i \'{itf}\' -j \'{jsonconf}\''''
        output = self.run(cmd)
        logger.info(output[0])
        logger.info(output[1])

    def ovs_add_bridge(self, br):
        logger.info(
            "[DROPLET {}]: Add ovs bridge {}".format(self.id, br))
        script = (f''' bash -c '\
ovs-vsctl add-br {br} && \
ip link set {br} up ' ''')
        self.run(script)

    def ovs_is_exist(self, br):
        cmd = 'ovs-vsctl br-exists {}'.format(br)
        return self.run(cmd)[0] == 0

    def ovs_add_port(self, br, port):
        logger.info(
            "[DROPLET {}]: ovs_add_port to {}".format(self.id, br))
        cmd = 'ovs-vsctl add-port {} {}'.format(br, port)
        self.run(cmd)

        cmd = f''' ovs-vsctl get Interface {port} ofport'''
        return self.run(cmd)[1].rstrip()

    def ovs_add_transit_flow(self, br, in_port, out_port):
        logger.info("[DROPLET {}]: ovs_add_transit_flow {}, {}, {}".format(
            self.id, br, in_port, out_port))
        cmd = f'''ovs-ofctl add-flow {br} priority=50,in_port={in_port},dl_type=0x800,actions=output:{out_port}'''
        self.run(cmd)

        cmd = f'''ovs-ofctl add-flow {br} priority=50,in_port={in_port},dl_type=0x806,actions=output:{out_port}'''
        self.run(cmd)

    def add_vxlan_ofrule(self, br, in_port, out_port, nw_dst):
        cmd = f'''ovs-ofctl add-flow {br} priority=100,in_port={in_port},dl_type=0x800,nw_dst={nw_dst},actions=output:{out_port}'''
        self.run(cmd)

        cmd = f'''ovs-ofctl add-flow {br} priority=100,in_port={in_port},dl_type=0x806,nw_dst={nw_dst},actions=output:{out_port}'''
        self.run(cmd)

    def ovs_create_vxlan_tun_itf(self, br, itf, vxlan_key, remote_ip):
        logger.info(
            "[DROPLET {}]: create_vxlan_tun_itf {}, {}".format(self.id, itf, remote_ip))
        cmd = f'''ovs-vsctl --may-exist \
add-port {br} {itf} \
-- set interface {itf} \
type=vxlan options:remote_ip={remote_ip} \
options:key={vxlan_key}'''
        self.run(cmd)

        cmd = f''' ovs-vsctl get Interface {itf} ofport'''
        return self.run(cmd)[1].rstrip()

    def ovs_create_geneve_tun_itf(self, br, itf, geneve_key, remote_ip):
        logger.info(
            "[DROPLET {}]: ovs_create_geneve_tun_itf {}, {}".format(self.id, itf, remote_ip))
        cmd = f'''ovs-vsctl --may-exist \
add-port {br} {itf} \
-- set interface {itf} \
type=geneve options:remote_ip={remote_ip} \
options:key={geneve_key}'''
        self.run(cmd)
        cmd = f''' ovs-vsctl get Interface {itf} ofport'''
        return self.run(cmd)[1].rstrip()

    def get_substrate_ep_json(self):
        """
        Get a substrate endpoint data to configure XDP programs to
        send packets to this droplet (no ARP for the moment!)
        """
        jsonconf = {
            "tunnel_id": "0",
            "ip": self.ip,
            "eptype": "0",
            "mac": self.mac,
            "veth": "",
            "remote_ips": [""],
            "hosted_iface": ""
        }
        return json.dumps(jsonconf)

    def run_from_root(self, cmd):
        ret_value = run_cmd(cmd)
        logger.debug(
            "[DROPLET {}]: running from root\n    command:\n {}, \n    exit_code: {},\n    output:\n {}".format(self.id, cmd, ret_value[0], ret_value[1]))
        return ret_value

    def run(self, cmd, detach=False):
        """
        Runs a command directly on the droplet
        """

        ret_value = None
        if (self.droplet_type == 'docker'):
            out = self.container.exec_run(cmd, detach=detach)
            if not detach:
                ret_value = (out.exit_code, out.output.decode("utf-8"))

        logger.info("[DROPLET {}]: running: {}".format(self.id, cmd))
        if (not detach and ret_value[0] == 1):
            logger.error("[DROPLET {}]: {}".format(self.id, ret_value[1]))

        if not detach:
            logger.debug(
                "[DROPLET {}]: running\n    command:\n {}, \n    exit_code: {},\n    output:\n {}".format(self.id, cmd, ret_value[0], ret_value[1]))

        return ret_value

    def _collect_logs(self):
        cmd = f'''
cp /var/log/syslog /trn_test_out/syslog_{self.ip}
        '''
        self.run(cmd)

    def _create_docker_container(self):
        """ Create and initialize a docker container.
        Assumes "buildbox:v2" image exist and setup on host
        """
        cwd = os.getcwd()

        # get a docker client
        docker_client = docker.from_env()
        docker_image = "buildbox:v2"
        mount_pnt = docker.types.Mount("/mnt/Transit",
                                       cwd,
                                       type='bind')

        mount_modules = docker.types.Mount("/lib/modules",
                                           "/lib/modules",
                                           type='bind')

        # Create the contrainer in previlaged mode
        container = docker_client.containers.create(
            docker_image, '/bin/bash', tty=True,
            stdin_open=True, auto_remove=False, mounts=[mount_pnt, mount_modules],
            privileged=True, cap_add=["SYS_PTRACE"],
            security_opt=["seccomp=unconfined"])
        container.start()
        container.reload()

        # Restart dependancy services
        container.exec_run("/etc/init.d/rpcbind restart")
        container.exec_run("/etc/init.d/rsyslog restart")
        container.exec_run("ip link set dev eth0 up mtu 9000")

        # We may need ovs for compatability tests
        container.exec_run("/etc/init.d/openvswitch-switch restart")

        # Create simlinks
        container.exec_run("ln -s /mnt/Transit/build/bin /trn_bin")
        container.exec_run("ln -s /mnt/Transit/build/xdp /trn_xdp")
        container.exec_run("ln -s /sys/fs/bpf /bpffs")
        container.exec_run(
            "ln - s /mnt/Transit/test/trn_func_tests/output /trn_test_out")

        # Run the transitd in the background
        container.exec_run("/trn_bin/transitd ",
                           detach=True)

        # Enable debug and tracing for the kernel
        container.exec_run(
            "mount -t debugfs debugfs /sys/kernel/debug")
        container.exec_run(
            "echo 1 > /sys/kernel/debug/tracing/tracing_on")

        # Enable core dumps (just in case!!)
        container.exec_run("ulimit -u")
        cmd = "echo '/mnt/Transit/core/core_{}_%e.%p' |\
 tee /proc/sys/kernel/core_pattern ".format(self.ip)
        container.exec_run(cmd)

        self.container = container
        self.ip = self.container.attrs['NetworkSettings']['IPAddress']
        self.mac = self.container.attrs['NetworkSettings']['MacAddress']

    def start_pcap(self):
        # Start a pcap to collect packets on eth0
        cmd = f''' bash -c \
'(/mnt/Transit/tools/xdpcap /bpffs/eth0_transit_pcap \
/trn_test_out/\
droplet_{self.ip}.pcap >/dev/null 2>&1 &\
)' '''
        self.run(cmd)

    def delete_container(self):
        if self.container:
            self.container.stop()
            self.container.remove()

    def __del__(self):
        self.unload_transit_xdp()

        self.run("killall5 -2")
        sleep(1)
        if 'NOCLEANUP' in os.environ:
            return
        self.delete_container()

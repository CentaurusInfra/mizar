import os
import sys
import json
import logging
import uuid
import pprint
import subprocess
import tempfile
from common.common import *
from common.constants import *
from store.operator_store import OprStore
from kubernetes.client import Configuration
from obj.endpoint import Endpoint
from obj.droplet import Droplet
from rpyc import Service
from socket import AF_INET
from pyroute2 import IPRoute, NetNS
from kubernetes import client, config, watch

logger = logging.getLogger()

def get_host_info():
	### Get the droplet IP/MAC
	cmd = 'ip addr show eth0 | grep "inet\\b" | awk \'{print $2}\' | cut -d/ -f1'
	r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	ip = r.stdout.read().decode().strip()

	cmd = 'ip addr show eth0 | grep "link/ether\\b" | awk \'{print $2}\' | cut -d/ -f1'
	r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	mac = r.stdout.read().decode().strip()

	cmd = 'hostname'
	r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	name = r.stdout.read().decode().strip()


	cmd = "ip link set dev eth0 xdpgeneric off"

	r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	output = r.stdout.read().decode().strip()
	logging.info("Removed existing XDP program: {}".format(output))

	cmd = "/trn_bin/transitd &"
	r = subprocess.Popen(cmd, shell=True)
	logging.info("Running transitd")

	config = '{"xdp_path": "/trn_xdp/trn_transit_xdp_ebpf_debug.o", "pcapfile": "/bpffs/transit_xdp.pcap"}'
	cmd = (f''' /trn_bin/transit -s {ip} load-transit-xdp -i eth0 -j '{config}' ''')

	r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	output = r.stdout.read().decode().strip()
	logging.info("Running load-transit-xdp: {}".format(output))

	logging.info("Droplet {} is ready".format(name))

	spec = {
		'ip': ip,
		'mac': mac,
		'itf': 'eth0',
		'status': OBJ_STATUS.droplet_status_init
		}

	return name, spec


class CniService(Service):
	config = None
	cert = ""
	ssl_ca_cert = None
	droplet = None
	store = OprStore()
	droplet_configured = False

	def configure_droplet(obj_api):
		if CniService.droplet_configured:
			return
		name, spec = get_host_info()
		droplet = Droplet(name, obj_api, CniService.store, spec)
		droplet.create_obj()
		CniService.droplet_configured = True
		return name

	def on_connect(self, conn):
		self.iproute = IPRoute()
		CniService.ssl_ca_cert = '/tmp/ca'
		f = open(CniService.ssl_ca_cert, 'w')
		f.write(CniService.cert)
		self._set_config()
		self.obj_api = client.CustomObjectsApi()
		self.configure_droplet()

	def _set_config(self):
		configuration = Configuration()
		configuration.host = CniService.config.host
		configuration.ssl_ca_cert = CniService.ssl_ca_cert
		configuration.api_key['authorization'] = CniService.config.api_key['authorization']
		Configuration.set_default(configuration)

	def __del__(self):
		self.iproute.close()

	def exposed_add(self, params):
		val = "Add service failed!"
		status = 1
		ep = self.get_or_create_ep(params)

		if ep.status != OBJ_STATUS.ep_status_provisioned:
			return val, status

		result = {
			"cniVersion": params.cni_version,
			"interfaces": [
				{
					"name": ep.veth_name,
					"mac": ep.mac,
					"sandbox": ep.netns
				}
			],
			"ips":[
				{
					"version": "4",
					"address": "{}/{}".format(ep.ip,ep.prefix),
					"gateway": ep.gw,
					"interface": 0
				}
			]
		}

		val = json.dumps(result)
		status = 0
		logger.info("cni service added {}".format(ep.name))
		return val, status

	def exposed_delete(self, params):
		val = "!!delete service!!"
		status = 1
		logger.info("cni service delete {}".format(params))
		return val, status

	def exposed_get(self, params):
		val = "!!get service!!"
		status = 1
		logger.info("cni service get {}".format(params))
		return val, status

	def exposed_version(self, params):
		val = "!!version service!!"
		status = 1
		logger.info("cni service version {}".format(params))
		return val, status

	def get_or_create_ep(self, params):

		logger.debug("Allocate endpoint name")
		name = ""
		if 'K8S_POD_NAME' in params.cni_args_dict:
			name = params.cni_args_dict['K8S_POD_NAME']
		name = 'simple-ep-' + name

		if CniService.store.contains_ep(name):
			return CniService.store.get_ep(name)

		ep = Endpoint(name, self.obj_api, CniService.store)

		# If not provided in Pod, use defaults
		# TODO: have it pod :)
		ep.set_vni(params.default_vni)
		ep.set_vpc(params.default_vpc)
		ep.set_net(params.default_net)

		ep.set_type(OBJ_DEFAULTS.ep_type_simple)
		ep.set_status(OBJ_STATUS.ep_status_init)
		ep.set_veth_name(params.interface)
		ep.set_droplet(CniService.droplet)
		ep.set_container_id(params.container_id)
		self.allocate_local_id(ep)

		ep.set_veth_name("eth-" + ep.local_id)
		ep.set_veth_peer("veth-" + ep.local_id)
		ep.set_netns("mizar-" + ep.local_id)


		iproute_ns = self.create_mizarnetns(params, ep)
		self.prepare_veth_pair(ep, iproute_ns, params)

		ep.create_obj()
		ep.watch_obj(self.ep_ready_fn)
		self.provision_endpoint(ep, iproute_ns)
		ep.set_status(OBJ_STATUS.ep_status_provisioned)
		ep.update_obj()

		return ep

	def provision_endpoint(self, ep, iproute_ns):
		#ip netns exec {ep.ns} sysctl -w net.ipv4.tcp_mtu_probing=2 && \
		#ip netns exec {ep.ns} ethtool -K veth0 tso off gso off ufo off && \
		#ip netns exec {ep.ns} ethtool --offload veth0 rx off tx off && \

		logging.debug("Add address to ep {}".format(ep.name))
		iproute_ns.addr('add', index=ep.veth_index, address=ep.ip, prefixlen=int(ep.prefix))

		logging.debug("Add route to default GW to ep {}".format(ep.name))
		iproute_ns.route('add', gateway=ep.gw)

	def ep_ready_fn(self, event, ep):
		name = event['object']['metadata']['name']
		status = event['object']['spec']['status']
		if name != ep.name:
			return False
		if status != OBJ_STATUS.ep_status_ready:
			return False
		spec = event['object']['spec']
		# Now get the gw, ip, and prefix
		ep.set_gw(spec['gw'])
		ep.set_ip(spec['ip'])
		ep.set_prefix(spec['prefix'])
		return True

	def allocate_local_id(self, ep):
		e = [1]
		v = [1]
		while len(e) or len(v):
			localid = ep.container_id[-8:]
			eth = "eth-" + localid
			veth = 'veth-' + localid
			e = self.iproute.link_lookup(ifname=eth)
			v = self.iproute.link_lookup(ifname=veth)

		ep.set_local_id(localid)
		logging.debug("Allocated ID for {} as {}".format(ep.name, localid))

	def create_mizarnetns(self, params, ep):
		os.makedirs('/var/run/netns/', exist_ok = True)
		f = os.listdir('/var/run/netns/')
		logging.debug("files ns {}".format(f))
		src = params.netns
		dst = '/var/run/netns/{}'.format(ep.netns)
		os.symlink(src, dst)
		logging.debug("Created namespace {} from {}".format(ep.netns, params.netns))
		return NetNS(ep.netns)


	def prepare_veth_pair(self, ep, iproute_ns, params):

		self.iproute.link('add', ifname=ep.veth_name, peer=ep.veth_peer, kind='veth')

		ep.set_veth_index(get_iface_index(ep.veth_name, self.iproute))
		ep.set_veth_peer_index(get_iface_index(ep.veth_peer, self.iproute))

		ep.set_mac(get_iface_mac(ep.veth_index, self.iproute))
		ep.set_veth_peer_mac(get_iface_mac(ep.veth_peer_index, self.iproute))

		logger.debug("Move interface {} to netns {}".format(ep.veth_name, ep.netns))
		self.iproute.link('set', index=ep.veth_index, net_ns_fd=ep.netns)

		logger.debug("Rename interface to {}".format(params.interface))
		ep.set_veth_name(params.interface)
		iproute_ns.link('set', index=ep.veth_index, ifname=params.interface)

		logging.info("Bring loopback device in netns {} up".format(ep.netns))
		lo_idx = self.iproute.link_lookup(ifname="lo")[0]
		iproute_ns.link('set', index=lo_idx, state='up')

		logging.info("Bring endpoint's interface {} up in netns {}".format(ep.veth_name, ep.netns))
		iproute_ns.link('set', index=ep.veth_index, state='up')

		logging.info("Bring veth interface {} up and set mtu to 9000".format(ep.veth_peer))
		self.iproute.link('set', index=ep.veth_peer_index, state='up', mtu=9000)




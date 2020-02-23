#!/usr/bin/python3
import os
import sys
import json
import logging
import uuid
import pprint
import subprocess
from socket import AF_INET
from pyroute2 import IPRoute, NetNS
from kubernetes import client, config, watch

logging.basicConfig(level=logging.INFO, filename='/tmp/cni.log')
sys.stderr = open('/tmp/cni.stderr', 'a')

class k8sParams:
	def __init__(self, stdin):
		#logging.info(stdin)
		self.command = os.environ.get("CNI_COMMAND") # ADD | DEL | VERSION
		self.container_id = os.environ.get("CNI_CONTAINERID")
		self.netns = os.environ.get("CNI_NETNS")
		self.container_pid = None
		if (self.netns != ""):
			self.container_pid =  self.netns.split("/")[2]
		self.interface = os.environ.get("CNI_IFNAME")
		self.cni_path = os.environ.get("CNI_PATH")
		self.cni_args = os.environ.get("CNI_ARGS")
		self.cni_args_dict = {}

		argarray = [i.split('=') for i in self.cni_args.split(';')]
		for a in argarray:
			self.cni_args_dict[a[0]] = a[1]

		# Load network configuration parameters
		config_json = json.loads(stdin)

		# expected parameters in the CNI specification:
		self.cni_version = config_json["cniVersion"]
		self.network_name = config_json["name"]
		self.plugin = config_json["type"]
		self.default_vpc = config_json["default_vpc"]
		self.default_net = config_json["default_net"]
		if "args" in config_json:
			self.args = config_json["args"]
		if "ipMasq" in config_json:
			self.ip_masq = config_json["ipMasq"]
			self.ipam = config_json["ipam"]
		if "dns" in config_json:
			self.dns = config_json["dns"]

		self.k8sconfig = config_json["k8sconfig"]

		logging.info("read params")
		cmd = 'hostname'
		r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		self.droplet = r.stdout.read().decode().strip()
		logging.info("done reading params {}".format(self.droplet))

class endpoint:
	def __init__(self, params, core_api, obj_api):
		self.params = params
		self.args = self.params.cni_args_dict
		self.core_api = core_api
		self.obj_api = obj_api
		self.interface = self.params.interface
		self.vpc = self.params.default_vpc
		self.net = self.params.default_net
		self.localid = 'NONE'
		self.netns = self.params.netns
		self.ip = "10.0.0.1"
		self.prefix = "32"
		self.gw = "10.0.0.1"
		self.interface_index = "0"
		self.status = "init"
		self.name = ""
		self.mac = ""
		self.veth = None
		self.veth_peer = None
		self.veth_peer_idx = -1
		self.veth_peer_mac = ""
		self.mizarnetns = None
		self.veth_prepared = False
		self.droplet = self.params.droplet
		if 'K8S_POD_NAME' in self.args:
			self.name = self.args['K8S_POD_NAME']
		self.name = 'simple-ep-' + self.name

	def get_ep_obj(self):
		self.obj = {
			"apiVersion": "mizar.com/v1",
			"kind": "Endpoint",
			"metadata": {
				"name": self.name
			},
			"spec": {
				"type": "simple",
				"status": self.status,
				"vpc": self.vpc,
				"net": self.net,
				"droplet": self.droplet,
				"mac": self.mac,
				"itf": self.interface,
				"veth": self.veth_peer,
				"netns": self.mizarnetns
			}
		}
		return self.obj

	def get_mizarnetns(self, iproute):
		if self.veth_prepared:
			return self.mizarnetns
		e = [1]
		v = [1]
		while len(e) or len(v):
			self.localid = self.params.container_id[-8:]
			eth = "eth-" + self.localid
			veth = 'veth-' + self.localid
			e = iproute.link_lookup(ifname=eth)
			v = iproute.link_lookup(ifname=veth)
		self.veth = "teth-" + self.localid
		self.veth_peer = "veth-" + self.localid
		self.mizarnetns = "mizar-" + self.localid

		os.makedirs('/var/run/netns/', exist_ok = True)
		src = self.netns
		dst = '/var/run/netns/{}'.format(self.mizarnetns)
		os.symlink(src, dst)

		logging.info("assiged_id {}".format(self.localid))
		return self.mizarnetns

	def prepare_veth_pair(self, iproute, iproute_ns):
		if self.veth_prepared:
			logging.info("looking for {} in {}".format(self.veth, self.mizarnetns))
			self.interface_index = iproute_ns.link_lookup(ifname=self.veth)[0]
			self.veth_peer_idx = iproute.link_lookup(ifname=self.veth_peer)[0]
			self.mac = self.get_iface_mac(self.interface_index, iproute_ns)
			self.veth_peer_mac = self.get_iface_mac(self.veth_peer_idx, iproute)
			logging.info("veth for {} exist on {}/{} veth:{} peer:{}".format(self.name, self.mizarnetns, self.netns, self.mac, self.veth_peer_mac))
			return

		iproute.link('add', ifname=self.veth, peer=self.veth_peer, kind='veth')
		self.interface_index = iproute.link_lookup(ifname=self.veth)[0]
		self.veth_peer_idx = iproute.link_lookup(ifname=self.veth_peer)[0]
		self.mac = self.get_iface_mac(self.interface_index, iproute)
		self.veth_peer_mac = self.get_iface_mac(self.veth_peer_idx, iproute)
		iproute.link('set', index=self.interface_index, net_ns_fd=self.mizarnetns)
		iproute_ns.link('set', index=self.interface_index, ifname=self.interface)

		logging.info("1/link_lookup")
		lo_idx = iproute.link_lookup(ifname="lo")[0]

		logging.info("2/link_set")
		iproute_ns.link('set',
			index=lo_idx,
			state='up')

		logging.info("3/link_set")
		iproute_ns.link('set',
			index=self.interface_index,
			state='up')

		logging.info("4/link_set {}: {}".format(self.veth_peer, self.veth_peer_idx))
		iproute.link('set',
			index=self.veth_peer_idx,
			state='up',
			mtu=9000)


		logging.info("veth for {} created on {}/{} veth:{} peer:{}".format(self.name, self.mizarnetns, self.netns, self.mac, self.veth_peer_mac))

	def get_iface_mac(self, idx, iproute):
		for (attr, val) in iproute.get_links(idx)[0]['attrs']:
			if attr == 'IFLA_ADDRESS':
				return val
		return None

	def create_endpoint_obj(self):

		try:

			body = self.obj_api.get_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			name=self.name)
			spec = body['spec']

			self.status = spec['status']
			self.vpc = spec['vpc']
			self.net = spec['net']
			self.droplet = spec['droplet']
			self.mac = spec['mac']
			self.interface = spec['itf']
			self.veth_peer = spec['veth']
			self.mizarnetns = spec['netns']
			self.prefix = spec['prefix']
			self.ip = spec['ip']
			self.veth = self.interface
			self.veth_prepared = True
			logging.info("Endpoint exist {}".format(spec))

		except:
			self.obj_api.create_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural="endpoints",
				body=self.get_ep_obj(),
			)
			logging.info("Endpoint created {}".format(self.name))


	def watch_endpoint_obj(self):
		watcher = watch.Watch()
		stream = watcher.stream(self.obj_api.list_namespaced_custom_object,
					group="mizar.com",
					version="v1",
					namespace="default",
					plural="endpoints",
					field_selector = "metadata.name={}".format(self.name),
					watch = True
				)

		for event in stream:
			name = event['object']['metadata']['name']
			status = event['object']['spec']['status']
			logging.info("!!Recieved name: {}, status: {}".format(name, status))
			if name != self.name:
				continue
			if status != "ready":
				continue
			logging.info("!!Filtered name: {}, status: {}".format(name, status))
			watcher.stop()
			spec = event['object']['spec']
			self.ip = spec['ip']
			self.prefix = spec['prefix']
			return True

	def is_endpoint_ready(self):
		return True

	def provision_endpoint(self, iproute, iproute_ns):
#ip netns exec {ep.ns} sysctl -w net.ipv4.tcp_mtu_probing=2 && \
#ip netns exec {ep.ns} ethtool -K veth0 tso off gso off ufo off && \
#ip netns exec {ep.ns} ethtool --offload veth0 rx off tx off && \

		logging.info("5/addr_add")
		iproute_ns.addr('add',
			index=self.interface_index,
        	address=self.ip,
        	prefixlen=int(self.prefix))

		logging.info("6/route_add")
		iproute_ns.route('add',
			gateway=self.gw)

	def finalize_provisioning(self):
		self.status = 'provisioned'
		body = self.obj_api.get_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			name=self.name)
		body['spec']['status'] = self.status
		logging.info("finalize Endpont {}".format(self.name))
		self.obj_api.patch_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			name=self.name,
			body=body,
		)
		logging.info("finalize endpint {}".format(self.name))


class cni:
	def __init__(self, params):
		self.params = params
		self.core_api=client.CoreV1Api()
		self.obj_api = client.CustomObjectsApi()
		self.iproute = IPRoute()
		self.iproute_ns = None

	def __del__(self):
		self.iproute.close()
		#if self.iproute_ns is not None:
		#	self.iproute_ns.close()

	def exec_add(self):
		#logging.info("add")
		#logging.info(self.params.cni_args_dict)
		ep = endpoint(self.params, self.core_api, self.obj_api)
		mizarnetns = ep.get_mizarnetns(self.iproute)
		self.iproute_ns = NetNS(mizarnetns)
		ep.prepare_veth_pair(self.iproute, self.iproute_ns)
		ep.create_endpoint_obj()
		if ep.watch_endpoint_obj():
			ep.provision_endpoint(self.iproute, self.iproute_ns)
		else:
			#TODO error handling
			pass
		ep.finalize_provisioning()
		logging.info("provisioned {}".format(ep.name))
		result = {
			"cniVersion": self.params.cni_version,
			"interfaces": [
				{
					"name": ep.interface,
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

		return json.dumps(result)

	def exec_delete(self):
		logging.info("delete")

	def exec_version(self):
		logging.info("version")

	def exec(self):
		switcher = {
			'ADD': self.exec_add,
			'DEL': self.exec_delete,
			'VERSION': self.exec_version
		}

		func = switcher.get(self.params.command, lambda: "Unsuported cni command")
		return func()


def main():

	params = k8sParams(''.join(sys.stdin.readlines()))
	config.load_kube_config(config_file=params.k8sconfig)
	c = cni(params)
	print(c.exec())

main()
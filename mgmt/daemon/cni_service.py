# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import json
import logging
import uuid
import pprint
import subprocess
import tempfile
import time
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
		CniService.droplet = Droplet(name, obj_api, CniService.store, spec)
		CniService.droplet.create_obj()
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
		val = ""
		status = 0
		self.delete_ep(params)
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

		start_time = time.time()
		ep = Endpoint(name, self.obj_api, CniService.store)

		# If not provided in Pod, use defaults
		# TODO: have it pod :)
		ep.set_vni(params.default_vni)
		ep.set_vpc(params.default_vpc)
		ep.set_net(params.default_net)

		ep.set_type(OBJ_DEFAULTS.ep_type_simple)
		ep.set_status(OBJ_STATUS.ep_status_init)
		ep.set_veth_name(params.interface)
		ep.set_droplet(CniService.droplet.name)
		ep.set_container_id(params.container_id)
		self.allocate_local_id(ep)

		ep.set_veth_name("eth-" + ep.local_id)
		ep.set_veth_peer("veth-" + ep.local_id)
		ep.set_netns("mizar-" + ep.local_id)
		ep.set_droplet_ip(CniService.droplet.ip)
		ep.set_droplet_mac(CniService.droplet.mac)
		ep.set_droplet_obj(CniService.droplet)

		iproute_ns = self.create_mizarnetns(params, ep)
		self.prepare_veth_pair(ep, iproute_ns, params)
		ep.load_transit_agent()

		ep.set_cnidelay(time.time() - start_time)
		ep.create_obj()
		ep.watch_obj(self.ep_ready_fn)
		self.provision_endpoint(ep, iproute_ns)
		ep.set_status(OBJ_STATUS.ep_status_provisioned)
		ep.set_provisiondelay(time.time() - start_time)
		ep.update_obj()
		CniService.store.update_ep(ep)

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
		if status != OBJ_STATUS.ep_status_provisioned:
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

	def delete_ep(self, params):
		if 'K8S_POD_NAME' in params.cni_args_dict:
			pod_name = params.cni_args_dict['K8S_POD_NAME']
			name = 'simple-ep-' + pod_name
			if CniService.store.contains_ep(name):
				ep = CniService.store.get_ep(name)
			else:
				return
		else:
			logger.debug("Pod name not found!!")
			return
		ep.delete_obj()
		logger.info("cni service delete {}".format(ep.name))
		CniService.store.delete_ep(ep.name)
		self.delete_mizarnetns(ep)
		self.delete_veth_pair(ep)

	def delete_mizarnetns(self, ep):
		os.remove("/var/run/netns/{}".format(ep.netns))
		logging.debug("Deleted namespace {}".format(ep.netns))

	def delete_veth_pair(self, ep):
		self.iproute.link('del', index=ep.veth_peer_index)
		logging.debug("Deleted veth-pair {}, from {}".format(ep.veth_peer, ep.netns))

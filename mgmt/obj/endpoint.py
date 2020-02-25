import logging
from common.constants import *
from kubernetes import watch

logger = logging.getLogger()

class Endpoint:
	def __init__(self, name, obj_api):
		self.name = name
		self.obj_api = obj_api

		# Initial values all none
		self.vpc = ""
		self.net = ""
		self.vni = ""
		self.status = ""
		self.gw = ""
		self.ip = ""
		self.prefix = ""
		self.mac = ""
		self.type = ""
		self.droplet = ""
		self.veth_peer = ""
		self.veth_name = ""
		self.netns = ""
		self.container_id = ""
		self.local_id = ""
		self.veth_index = ""
		self.veth_peer_index = ""
		self.mac = ""
		self.veth_peer_mac = ""

		# Misc obj
		# self.droplet_obj = None

	def get_obj_spec(self):
		self.obj = {
				"type": self.type,
				"status": self.status,
				"vpc": self.vpc,
				"net": self.net,
				"ip": self.ip,
				"gw": self.gw,
				"mac": self.mac,
				"vni": self.vni,
				"droplet": self.droplet,
				"prefix": self.prefix,
				"itf": self.veth_name,
				"veth": self.veth_peer,
				"netns": self.netns,
		}

		return self.obj

	# K8s APIs
	def create_obj(self):
		try:
			body = self.obj_api.get_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural="endpoints",
				name=self.name)
			spec = body['spec']
			self.type = spec['type']
			self.status = spec['status']
			self.vpc = spec['vpc']
			self.net = spec['net']
			self.ip = spec['ip']
			self.gw = spec['gw']
			self.mac = spec['mac']
			self.vni = spec['vni']
			self.droplet = spec['droplet']
			self.prefix = spec['prefix']
			self.veth_name = spec['itf']
			self.veth_peer = spec['veth']
			self.netns = spec['netns']

		except:
			body = {
				"apiVersion": "mizar.com/v1",
				"kind": "Endpoint",
				"metadata": {
					"name": self.name
				},
				"spec": self.get_obj_spec()
			}

			self.obj_api.create_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural="endpoints",
				body=body,
			)
			logging.debug("Created endpoint {}".format(self.name))


	def update_obj(self):
		body = self.obj_api.get_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			name=self.name)
		body['spec'] = self.get_obj_spec()
		self.obj_api.patch_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			name=self.name,
			body=body,
		)


	def delete_obj(self):
		pass

	def watch_obj(self, watch_callback):
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
			if watch_callback(event, self):
				watcher.stop()
				return

	# Setters
	def set_vpc(self, vpc):
		self.vpc = vpc

	def set_net(self, net):
		self.net = net

	def set_vni(self, vni):
		self.vni = vni

	def set_status(self, status):
		self.status = status

	def set_gw(self, gw):
		self.gw = gw

	def set_ip(self, ip):
		self.ip = ip

	def set_prefix(self, prefix):
		self.prefix = prefix

	def set_mac(self, mac):
		self.mac = mac

	def set_type(self, eptype):
		self.type = eptype

	def set_droplet(self, droplet):
		self.droplet = droplet

	def set_droplet_obj(self, droplet_obj):
		self.droplet_obj = droplet_obj

	def set_veth_peer(self, veth_peer):
		self.veth_peer = veth_peer

	def set_veth_name(self, veth_name):
		self.veth_name = veth_name

	def set_netns(self, netns):
		self.netns = netns

	def set_container_id(self, container_id):
		self.container_id = container_id

	def set_local_id(self, local_id):
		self.local_id = local_id

	def set_veth_index(self, veth_index):
		self.veth_index = veth_index

	def set_veth_peer_index(self, veth_peer_index):
		self.veth_peer_index = veth_peer_index

	def set_veth_peer_mac(self, veth_peer_mac):
		self.veth_peer_mac = veth_peer_mac


############
	def update_object(self):
		body = self.obj_api.get_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			name=self.name)
		body['spec'] = self.get_obj_spec()
		logger.info("updating Endpont {}".format(self.name))
		self.obj_api.patch_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			name=self.name,
			body=body,
		)
		logger.info("updated endpint {}".format(self.name))


	def get_veth_peer(self):
		return self.veth_peer

	def get_veth_name(self):
		return self.veth_name

	def get_tunnel_id(self):
		return str(self.vni)

	def get_ip(self):
		return str(self.ip)

	def get_eptype(self):
		if self.type == ep_type_simple:
			return str(CONSTANTS.TRAN_SIMPLE_EP)

	def get_mac(self):
		return str(self.mac)

	def get_remote_ips(self):
		remote_ips = []
		remote_ips = self.droplet_obj and [str(self.droplet_obj.ip)]
		return remote_ips
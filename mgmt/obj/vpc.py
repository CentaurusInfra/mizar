import logging
import random
from common.constants import *
from common.common import *
from common.cidr import Cidr
from obj.divider import Divider
from kubernetes.client.rest import ApiException

logger = logging.getLogger()

class Vpc(object):
	def __init__(self, name, obj_api, opr_store, spec=None):
		self.name = name
		self.vni = OBJ_DEFAULTS.default_vpc_vni
		self.cidr = Cidr(OBJ_DEFAULTS.default_net_prefix, OBJ_DEFAULTS.default_net_ip)
		self.n_dividers = OBJ_DEFAULTS.default_n_dividers
		self.n_allocated_dividers = 0
		self.obj_api = obj_api
		self.status = OBJ_STATUS.vpc_status_init
		self.dividers = {}
		self.networks = {}
		self.store = opr_store
		if spec is not None:
			self.set_obj_spec(spec)

	def get_obj_spec(self):
		self.obj = {
			"ip": self.cidr.ip,
			"prefix": self.cidr.prefixlen,
			"vni": self.vni,
			"dividers": self.n_dividers,
			"status": self.status
		}

		return self.obj

	def set_obj_spec(self, spec):
		self.status = spec['status']
		self.vni = spec['vni']
		self.n_dividers = int(spec['dividers'])
		ip = spec['ip']
		prefix = spec['prefix']
		self.cidr = Cidr(prefix, ip)

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "vpcs"

	def get_kind(self):
		return "Vpc"

	def store_update_obj(self):
		self.store.update_vpc(self)

	def store_delete_obj(self):
		self.store.delete_vpc(self.name)

	def create_obj(self):
		return kube_create_obj(self)

	def update_obj(self):
		return kube_update_obj(self)

	def delete_obj(self):
		return kube_delete_obj(self)

	def watch_obj(self, watch_callback):
		return kube_watch_obj(self, watch_callback)

	def set_vni(self, vni):
		self.vni = vni

	def set_status(self, status):
		self.status = status

	def update_divider(self, droplet):
		logger.info("Update dividers {} for vpc".format(droplet.name, self.name))
		if droplet.name in self.dividers:
			return True

		self.dividers[droplet.name] = droplet
		divider_name = self.name +'-divider-' + droplet.name

		divider_spec = {
			"vpc": self.name,
			"mac": droplet.mac,
			"ip": droplet.ip,
			"status": OBJ_STATUS.divider_status_init,
			"droplet": droplet.name
		}

		div = Divider(divider_name, self.obj_api, self.store, divider_spec)
		div.create_obj()
		self.n_allocated_dividers += 1

	def delete_divider(self, droplet):
		pass
##
	def get_network(self, name):
		if name in self.networks:
			return self.networks[name]
		return None

	def update_network(self, name, network):
		self.networks[name]=network
		logger.info("networks {}".format(self.networks.keys()))

	def delete_network(self, network):
		pass

	def update_bouncer(self, network, bouncer):
		pass

	def delete_bouncer(self, network, bouncer):
		pass

	def update_simple_endpoint(self, ep):
		logger.info("update_simple_endpoint {} of vpc {}".format(ep.name, self.name))
		net_obj = self.get_network(ep.net)
		net_obj.update_simple_endpoint(ep)
		pass

	def delete_simple_endpoint(self):
		pass

	def update_host_endpoint(self):
		pass

	def delete_host_endpoint(self):
		pass

	def update_scaled_endpoint(self):
		pass

	def delete_scaled_endpoint(self):
		pass

import logging
import random
import uuid
from common.rpc import TrnRpc
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
		self.status = get_spec_val('status', spec)
		self.vni = get_spec_val('vni', spec)
		self.n_dividers = int(get_spec_val('dividers', spec, OBJ_DEFAULTS.default_n_dividers))
		ip = get_spec_val('ip', spec, OBJ_DEFAULTS.default_net_ip)
		prefix = get_spec_val('prefix', spec, OBJ_DEFAULTS.default_net_prefix)
		self.cidr = Cidr(prefix, ip)

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "vpcs"

	def get_kind(self):
		return "Vpc"

	def store_update_obj(self):
		if self.store is None:
			return
		self.store.update_vpc(self)

	def store_delete_obj(self):
		if self.store is None:
			return
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

	def create_divider(self):
		logger.info("Create divider for vpc {}".format(self.name))
		u = str(uuid.uuid4())
		divider_name = self.name +'-d-' + u
		d = Divider(divider_name, self.obj_api, None)
		d.set_vpc(self.name)
		d.set_vni(self.vni)
		self.dividers[divider_name] = d
		d.create_obj()

	def delete_divider(self):
		logger.info("Delete divider for net {}".format(self.name))
		d = self.dividers.pop(random.choice(list(self.dividers.keys())))
		d.delete_obj()

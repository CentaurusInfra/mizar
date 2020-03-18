import logging
from common.rpc import TrnRpc
from common.constants import *
from common.common import *

logger = logging.getLogger()

class Bouncer(object):
	def __init__(self, name, obj_api, opr_store, spec=None):
		self.name = name
		self.obj_api = obj_api
		self.store = opr_store
		self.droplet = ""
		self.vpc = ""
		self.net = ""
		self.ip = ""
		self.mac = ""
		self.eps = set()
		self.dividers = set()
		self.status = OBJ_STATUS.bouncer_status_init
		self.scaled_ep_obj = '/trn_xdp/trn_transit_scaled_endpoint_ebpf_debug.o'
		if spec is not None:
			self.set_obj_spec(spec)

	@property
	def rpc(self):
		return TrnRpc(self.ip, self.mac)

	def get_obj_spec(self):
		self.obj = {
			"vpc": self.vpc,
			"net": self.net,
			"ip": self.ip,
			"mac": self.mac,
			"status": self.status,
			"droplet": self.droplet
		}

		return self.obj

	def set_obj_spec(self, spec):
		self.status = get_spec_val('status', spec)
		self.vpc = get_spec_val('vpc', spec)
		self.net = get_spec_val('net', spec)
		self.ip = get_spec_val('ip', spec)
		self.mac = get_spec_val('mac', spec)
		self.droplet = get_spec_val('droplet', spec)

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "bouncers"

	def get_kind(self):
		return "Bouncer"

	def store_update_obj(self):
		if self.store is None:
			return
		self.store.update_bouncer(self)

	def store_delete_obj(self):
		if self.store is None:
			return
		self.store.delete_bouncer(self.name)

	def create_obj(self):
		return kube_create_obj(self)

	def update_obj(self):
		return kube_update_obj(self)

	def delete_obj(self):
		return kube_delete_obj(self)

	def watch_obj(self, watch_callback):
		return kube_watch_obj(self, watch_callback)

	def set_status(self, status):
		self.status = status

	def update_eps(self, eps):
		self.eps = self.eps.union(eps)
		for e in eps:
			if e.type == OBJ_DEFAULTS.ep_type_simple:
				self._update_ep(e)
			elif e.type == OBJ_DEFAULTS.ep_type_scaled:
				self._update_scaled_ep(e)

	def _update_ep(self, ep):
		self.rpc.update_ep(ep)
		self.rpc.update_substrate_ep(ep.droplet_ip, ep.droplet_mac)

	def _update_scaled_ep(self, ep):
		self.rpc.update_ep(ep)
		self.rpc.load_transit_xdp_pipeline_stage(CONSTANTS.ON_XDP_SCALED_EP,
			self.scaled_ep_obj)

	def update_dividers(self, dividers):
		self.dividers = self.dividers.union(dividers)

	def set_vpc(self, vpc):
		self.vpc = vpc

	def set_net(self, net):
		self.net = net

	def set_droplet(self, droplet):
		self.droplet = droplet.name
		self.ip = droplet.ip
		self.mac = droplet.mac

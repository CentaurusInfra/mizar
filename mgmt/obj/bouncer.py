import logging
from common.rpc import TrnRpc
from common.constants import *
from common.common import *
from common.cidr import Cidr

logger = logging.getLogger()

class Bouncer(object):
	def __init__(self, name, obj_api, opr_store, spec=None):
		self.name = name
		self.obj_api = obj_api
		self.store = opr_store
		self.droplet = ""
		self.droplet_obj = None
		self.vpc = ""
		self.vni = ""
		self.nip = ""
		self.net_prefixlen = ""
		self.net = ""
		self.ip = ""
		self.mac = ""
		self.eps = {}
		self.dividers = {}
		self.known_substrates = {}
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

	def get_divider_ips(self):
		return [d.ip for d in self.dividers.values()]

	def get_nip(self):
		return self.nip

	def get_prefixlen(self):
		return self.net_prefixlen

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
		for ep in eps:
			if ep.name not in self.eps.keys():
				logger.info("EEP: Updated")
				self.eps[ep.name] = ep
				self._update_ep(ep)
				self.droplet_obj.update_substrate(ep.name)

	def _update_ep(self, ep):
		self.rpc.update_ep(ep)

	def _update_scaled_ep(self, ep):
		self.rpc.update_ep(ep)
		self.rpc.load_transit_xdp_pipeline_stage(CONSTANTS.ON_XDP_SCALED_EP,
			self.scaled_ep_obj)

	def update_dividers(self, dividers):
		self.dividers = self.dividers.union(dividers)

	def update_vpc(self, dividers, add=True): # Fix this
		for divider in dividers:
			if add:
				logger.info("Divider added: {}".format(divider.name))
				self.dividers[divider.name] = divider
				self.droplet_obj.update_substrate(divider.name)
			else:
				logger.info("Divider removed: {}".format(divider.name))
				self.dividers[divider.name] = divider
				self.droplet_obj.delete_substrate(divider.name)
		self.droplet_obj.update_vpc(self)

	def delete_vpc(self): # Fix this
		for name in self.dividers.keys():
			divider = self.dividers.pop(name)
			self.droplet_obj.delete_substrate(divider)
		self.droplet_obj.delete_vpc(self)

	def set_vpc(self, vpc):
		self.vpc = vpc

	def set_net(self, net):
		self.net = net

	def set_vni(self, vni):
		self.vni = vni

	def set_cidr(self, cidr):
		self.nip = str(cidr.ip)
		self.net_prefixlen = str(cidr.prefixlen)

	def set_droplet(self, droplet):
		self.droplet_obj = droplet
		self.droplet = droplet.name
		self.ip = droplet.ip
		self.mac = droplet.mac

	def delete_eps(self, eps):
		for ep in eps:
			if ep.name in self.eps.keys():
				self.eps.pop(ep.name)
				self._delete_ep(ep)

	def _delete_ep(self, ep):
		self.rpc.delete_ep(ep)
		self.droplet_obj.delete_substrate(ep.name)


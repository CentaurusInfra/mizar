
import logging
from kubernetes.client.rest import ApiException

logger = logging.getLogger()

class Ftn(object):
	def __init__(self, obj_api, opr_store, spec=None):
		self.obj_api = obj_api
		self.store = opr_store
		self.droplet_obj = None
		self.vpc = ""
		self.vni = ""
		self.nip = ""
		self.prefix = ""
		self.net = ""
		self.status = OBJ_STATUS.ftn_status_init
		self.scaled_ep_obj = '/trn_xdp/trn_transit_scaled_endpoint_ebpf_debug.o'
		if spec is not None:
			self.set_obj_spec(spec)

	@property
	def rpc(self):
		return TrnRpc(self.ip, self.mac)

	def get_obj_spec(self):
		self.obj = {
			"name": self.name,
			"ip": self.ip,
			"droplet": self.droplet,
			"mac": self.mac,
			"chains": self.chains,
			"nextnode": self.nextnode,
			"status": self.status
		}
		return self.obj

	def set_obj_spec(self, spec):
		self.name = get_spec_val('name', spec)
		self.ip = get_spec_val('ip', spec)
		self.droplet = get_spec_val('droplet', spec)
		self.mac = get_spec_val('mac', spec)
		self.chains = get_spec_val('chains', spec)
		self.nextnode = get_spec_val('nextnode', spec)
		self.status = get_spec_val('status', spec)

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "ftns"

	def get_kind(self):
		return "Ftn"

	def get_ip(self):
		return self.ip

	def get_chains(self):
		return self.chains

	def get_nextnode(self):
		return self.nextnode

	def store_update_obj(self):
		if self.store is None:
			return
		self.store.update_ftn(self)

	def store_delete_obj(self):
		if self.store is None:
			return
		self.store.delete_ftn(self.name)

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

	def load_transit_xdp_pipeline_stage(self):
		self.rpc.load_transit_xdp_pipeline_stage(CONSTANTS.ON_XDP_SCALED_EP,
			self.scaled_ep_obj)

	def set_droplet(self, droplet):
		self.droplet_obj = droplet
		self.droplet = droplet.name
		self.ip = droplet.ip
		self.mac = droplet.mac

	def delete_eps(self, eps):
		for ep in eps:
			if ep.name in self.eps.keys():
				self.eps.pop(ep.name)
				if ep.type == OBJ_DEFAULTS.ep_type_simple:
					self._delete_ep(ep)
				if ep.type == OBJ_DEFAULTS.ep_type_scaled:
					self._delete_scaled_ep(ep)

	def _delete_ep(self, ep):
		self.droplet_obj.delete_ep(self.name, ep)
		self.droplet_obj.delete_substrate(ep)
		ep.droplet_obj.delete_ep(ep.name, ep)

	def _delete_scaled_ep(self, ep):
		self.droplet_obj.delete_ep(self.name, ep)

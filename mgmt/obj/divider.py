import logging
import luigi
from common.rpc import TrnRpc
from common.constants import *
from common.common import *

logger = logging.getLogger()

class Divider(object):
	def __init__(self, name, obj_api, opr_store, spec=None):
		self.name = name
		self.obj_api = obj_api
		self.store = opr_store
		self.vpc = ""
		self.vni = ""
		self.ip = ""
		self.mac = ""
		self.droplet = ""
		self.droplet_obj = None
		self.bouncers = {}
		self.status = OBJ_STATUS.divider_status_init
		if spec is not None:
			self.set_obj_spec(spec)

	@property
	def rpc(self):
		return TrnRpc(self.ip, self.mac)

	def get_obj_spec(self):
		self.obj = {
			"vpc": self.vpc,
			"vni": self.vni,
			"mac": self.mac,
			"ip": self.ip,
			"status": self.status,
			"droplet": self.droplet
		}

		return self.obj

	def set_obj_spec(self, spec):
		self.status = get_spec_val('status', spec)
		self.vpc = get_spec_val('vpc', spec)
		self.ip = get_spec_val('ip', spec)
		self.mac = get_spec_val('mac', spec)
		self.droplet = get_spec_val('droplet', spec)

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "dividers"

	def get_kind(self):
		return "Divider"

	def store_update_obj(self):
		if self.store is None:
			return
		self.store.update_divider(self)

	def store_delete_obj(self):
		if self.store is None:
			return
		self.store.delete_divider(self.name)

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

	def set_vpc(self, vpc):
		self.vpc = vpc

	def set_vni(self, vni):
		self.vni = vni

	def set_droplet(self, droplet):
		self.droplet_obj = droplet
		self.droplet = droplet.name
		self.ip = droplet.ip
		self.mac = droplet.mac

	def update_net(self, net, add=True):
		for bouncer in list(net.bouncers.values()):
			if add:
				if bouncer.name not in self.bouncers.keys():
					logger.info("Bouncer {} added for Net {}".format(bouncer.name, net.name))
					self.bouncers[bouncer.name] = bouncer
					self.droplet_obj.update_substrate(bouncer)
			else:
				if bouncer.name in self.bouncers.keys():
					logger.info("Bouncer {} removed from Net {}".format(bouncer.name,net.name))
					self.bouncers[bouncer.name] = bouncer
					self.droplet_obj.delete_substrate(bouncer)
		self.droplet_obj.update_net(net)

	def delete_net(self, net):
		for name in net.bouncers.values():
			bouncer = self.bouncers.pop(name)
			self.droplet_obj.delete_substrate(bouncer)
		self.droplet_obj.delete_net(net)

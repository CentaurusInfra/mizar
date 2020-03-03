import logging
import json
from common.rpc import TrnRpc
from common.constants import *
from common.common import *
from common.common import run_cmd

logger = logging.getLogger()


class Droplet(object):

	def __init__(self, name, obj_api, opr_store, spec=None):
		self.name = name
		self.obj_api = obj_api
		self.store = opr_store
		self.ip = ""
		self.mac = ""
		self.phy_itf = 'eth0'
		self.status = OBJ_STATUS.droplet_status_init
		if spec is not None:
			self.set_obj_spec(spec)

	@property
	def rpc(self):
		return TrnRpc(self.ip, self.mac)

	def get_obj_spec(self):
		self.obj = {
			"mac": self.mac,
			"ip": self.ip,
			"status": self.status,
			"itf": self.phy_itf
		}

		return self.obj

	def set_obj_spec(self, spec):
		self.status = get_spec_val('status', spec)
		self.mac = get_spec_val('mac', spec)
		self.ip = get_spec_val('ip', spec)
		self.phy_itf = get_spec_val('itf', spec)

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "droplets"

	def get_kind(self):
		return "Droplet"

	def store_update_obj(self):
		if self.store is None:
			return
		self.store.update_droplet(self)

	def store_delete_obj(self):
		if self.store is None:
			return
		self.store.delete_droplet(self.name)

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

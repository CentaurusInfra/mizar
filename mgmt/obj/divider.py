import logging
from common.constants import *
from common.common import *

logger = logging.getLogger()

class Divider(object):
	def __init__(self, name, obj_api, opr_store, spec=None):
		self.name = name
		self.obj_api = obj_api
		self.store = opr_store
		self.vpc = ""
		self.ip = ""
		self.mac = ""
		self.droplet = ""
		self.status = OBJ_STATUS.divider_status_init
		if spec is not None:
			self.set_obj_spec(spec)

	def get_obj_spec(self):
		self.obj = {
			"vpc": self.vpc,
			"mac": self.mac,
			"ip": self.ip,
			"status": self.status,
			"droplet": self.droplet
		}

		return self.obj

	def set_obj_spec(self, spec):
		self.status = spec['status']
		self.vpc = spec['vpc']
		self.ip = spec['ip']
		self.mac = spec['mac']
		self.droplet = spec['droplet']

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "dividers"

	def get_kind(self):
		return "Divider"

	def create_obj(self):
		return kube_create_obj(self)

	def update_obj(self):
		return kube_update_obj(self)

	def delete_obj(self):
		return kube_delete_obj(self)

	def watch_obj(self, watch_callback):
		return kube_watch_obj(self, watch_callback)

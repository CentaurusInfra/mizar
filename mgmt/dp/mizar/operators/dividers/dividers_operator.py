import random
import uuid
from kubernetes import client, config
from common.constants import *
from common.common import *
from obj.bouncer import Bouncer
from obj.divider import Divider
from store.operator_store import OprStore
import logging

logger = logging.getLogger()

class DividerOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(DividerOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def query_existing_dividers(self):
		logger.info("divider on_startup")
		def list_dividers_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped Divider {}".format(name))
			d = Divider(name, self.obj_api, self.store, spec)
			if d.status == OBJ_STATUS.divider_status_provisioned:
				self.store_update(d)

		kube_list_obj(self.obj_api, RESOURCES.droplets, list_dividers_obj_fn)

	def get_divider_tmp_obj(self, name, spec):
		return Divider(name, self.obj_api, None, spec)

	def get_divider_stored_obj(self, name, spec):
		return Divider(name, self.obj_api, self.store, spec)

	def store_update(self, divider):
		self.store.update_divider(divider)

	def set_divider_provisioned(self, div):
		div.set_status(OBJ_STATUS.divider_status_provisioned)
		div.update_obj()

	def update_bouncer_with_dividers(self, bouncer, net): # Fix this
		dividers = self.store.get_dividers_of_vpc(bouncer.vpc)
		for d in dividers:
			d.update_net(net)

	def delete_bouncer_from_dividers(self, bouncer, net): # Fix this
		dividers = self.store.get_dividers_of_vpc(bouncer.vpc)
		for d in dividers:
			d.update_net(net, False)

	def update_net(self, net, dividers=None): # Fix this
		if not dividers:
			dividers = self.store.get_dividers_of_vpc(net.vpc)
		logger.info("Len of dividers is {}".format(len(dividers)))
		for d in dividers:
			d.update_net(net)

	def delete_net(self, net): # Fix this
		dividers = self.store.get_dividers_of_vpc(net.vpc)
		for d in dividers:
			d.delete_net(net)

	def update_vpc(self, bouncer): # Fix this
		dividers = self.store.get_dividers_of_vpc(bouncer.vpc)
		logger.info("Len of dividers is {}".format(len(dividers)))
		bouncer.update_vpc(dividers)

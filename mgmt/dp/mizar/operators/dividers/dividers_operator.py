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
				self.store.update_divider(d)

		kube_list_obj(self.obj_api, RESOURCES.droplets, list_dividers_obj_fn)

	def get_divider_tmp_obj(self, name, spec):
		return Divider(name, self.obj_api, None, spec)

	def get_divider_stored_obj(self, name, spec):
		return Divider(name, self.obj_api, self.store, spec)

	def on_divider_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_divider_provisioned {}".format(spec))
		d = Divider(name, self.obj_api, self.store, spec)
		self.store.update_divider(d)

	def set_divider_provisioned(self, div):
		div.set_status(OBJ_STATUS.divider_status_provisioned)
		div.update_obj()

	def on_bouncer_endpoint_ready(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_bouncer_endpoint_ready {}".format(spec))
		b = Bouncer(name, self.obj_api, None, spec)
		dividers = self.store.get_dividers_of_vpc(b.vpc)
		b.update_dividers(dividers)
		for d in dividers:
			d.update_bouncers(set([b]))
		b.set_status(OBJ_STATUS.bouncer_status_provisioned)
		b.update_obj()

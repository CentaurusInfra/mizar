import random
import uuid
from kubernetes import client, config
from common.constants import *
from common.common import *
from obj.vpc import Vpc
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

	def on_startup(self, logger, **kwargs):
		logger.info("divider on_startup")
		def list_dividers_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped Divider {}".format(name))
			d = Divider(name, self.obj_api, self.store, spec)
			self.store.update_divider(d)

		kube_list_obj(self.obj_api, RESOURCES.droplets, list_dividers_obj_fn)

	def on_divider_provisioned(body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_divider_provisioned {}".format(spec))
		d = Divider(name, self.obj_api, self.store, spec)
		self.store.update_divider(d)

	def on_bouncer_endpoint_ready(body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_bouncer_endpoint_ready {}".format(spec))
		b = Bouncer(name, self.obj_api, None, spec)
		dividers = self.store.get_dividers_of_vpc(b.vpc)
		b.add_dividers(dividers)
		for d in dividers:
			d.add_bouncer(b)
		b.set_status(OBJ_STATUS.bouncer_status_provisioned)
		b.update_obj()

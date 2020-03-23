import random
import logging
from kubernetes import client, config
from obj.bouncer import Bouncer
from obj.divider import Divider
from obj.endpoint import Endpoint
from common.constants import *
from common.common import *
from obj.net import Net
from store.operator_store import OprStore

logger = logging.getLogger()

class BouncerOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(BouncerOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def query_existing_bouncers(self):
		logger.info("bouncer on_startup")
		def list_bouncers_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped Bouncer {}".format(name))
			b = Bouncer(name, self.obj_api, self.store, spec)
			self.store_update(b)

		kube_list_obj(self.obj_api, RESOURCES.droplets, list_bouncers_obj_fn)

	def get_bouncer_tmp_obj(self, name, spec):
		return Bouncer(name, self.obj_api, None, spec)

	def get_bouncer_stored_obj(self, name, spec):
		return Bouncer(name, self.obj_api, self.store, spec)

	def store_update(self, b):
		self.store.update_bouncer(b)

	def set_bouncer_provisioned(self, bouncer):
		bouncer.set_status(OBJ_STATUS.bouncer_status_provisioned)
		bouncer.update_obj()

	def update_bouncers_with_divider(self, div):
		bouncers = self.store.get_bouncers_of_vpc(div.vpc)
		for b in bouncers.values():
			logger.info("BB {}".format(b.name))
			b.update_vpc(set([div]))

	def delete_divider_from_bouncers(self, div):
		bouncers = self.store.get_bouncers_of_vpc(div.vpc)
		for b in bouncers.values():
			b.update_vpc(set([div]), False)

	def update_endpoint_with_bouncers(self, ep):
		bouncers = self.store.get_bouncers_of_net(ep.net)
		eps = set([ep])
		for key in bouncers:
			bouncers[key].update_eps(eps)
		ep.update_bouncers(bouncers)

	def delete_endpoint_from_bouncers(self, ep):
		bouncers = self.store.get_bouncers_of_net(ep.net)
		eps = set([ep])
		for key in bouncers:
			bouncers[key].delete_eps(eps)
		self.store.update_bouncers_of_net(ep.net, bouncers)
		# No need to delete agent info, it gets deleted with agent unload

	def delete_vpc(self, bouncer):
		bouncer.delete_vpc()
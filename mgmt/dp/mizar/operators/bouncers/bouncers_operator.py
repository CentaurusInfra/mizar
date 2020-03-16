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

	def on_bouncer_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_bouncer_provisioned {}".format(spec))
		b = Bouncer(name, self.obj_api, self.store, spec)
		self.store.update_bouncer(b)

	def on_divider_placed(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_divider_placed {}".format(spec))
		# divider.bouncers = net.get_all_bouncers (bouncers_opr)
		div = Divider(name, self.obj_api, None, spec)
		bouncers = self.store.get_bouncers_of_vpc(div.vpc)
		div.update_bouncers(set(bouncers))
		for b in bouncers:
			b.update_dividers(set([div]))
		div.set_status(OBJ_STATUS.divider_status_provisioned)
		div.update_obj()

	def set_bouncer_provisioned(self, bouncer):
		bouncer.set_status(OBJ_STATUS.bouncer_status_provisioned)
		bouncer.update_obj()

	def update_bouncers_with_divider(self, div):
		bouncers = self.store.get_bouncers_of_vpc(div.vpc)
		div.update_bouncers(set(bouncers))
		for b in bouncers:
			b.update_dividers(set([div]))

	def on_endpoints_allocated(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_endpoints_allocated {}".format(spec))
		ep = Endpoint(name, self.obj_api, None, spec)
		bouncers = self.store.get_bouncers_of_net(ep.net)
		eps = set([ep])
		for b in bouncers:
			b.update_eps(eps)
		ep.update_bouncers(bouncers)
		ep.update_md()
		ep.set_status(OBJ_STATUS.ep_status_provisioned)
		ep.update_obj()

	def update_endpoint_with_bouncers(self, ep):

		bouncers = self.store.get_bouncers_of_net(ep.net)
		eps = set([ep])

		for key in bouncers:
			bouncers[key].update_eps(eps)
		self.store.update_bouncers_of_net(ep.net, bouncers)
		for bouncer in self.store.get_bouncers_of_net(ep.net).values():
			logger.info("Bouncer: {}".format(bouncer.name))
			for ep in bouncer.eps:
				logger.info("Ep is {}".format(ep.name))

		if ep.type == OBJ_DEFAULTS.ep_type_simple:
			ep.update_bouncers(bouncers)
			ep.update_md()

	def delete_endpoint_with_bouncers(self, ep):
		bouncers = self.store.get_bouncers_of_net(ep.net)
		for bouncer in self.store.get_bouncers_of_net(ep.net).values():
			logger.info("Before delete Bouncer: {}".format(bouncer.name))
			for ep in bouncer.eps:
				logger.info("Ep is {}".format(ep.name))
		eps = set([ep])
		for key in bouncers:
			bouncers[key].delete_eps(eps)
		self.store.update_bouncers_of_net(ep.net, bouncers)
		for bouncer in self.store.get_bouncers_of_net(ep.net).values():
			logger.info("After delete Bouncer: {}".format(bouncer.name))
			for ep in bouncer.eps:
				logger.info("Ep is {}".format(ep.name))
		# No need to delete agent info, it gets deleted with agent unload

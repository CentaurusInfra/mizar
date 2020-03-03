import logging
from kubernetes import client, config
from obj.endpoint import Endpoint
from obj.bouncer import Bouncer
from common.constants import *
from common.common import *
from store.operator_store import OprStore

logger = logging.getLogger()

class EndpointOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(EndpointOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_startup(self, logger, **kwargs):
		def list_endpoint_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped {}".format(name))
			ep = Endpoint(name, self.obj_api, self.store, spec)
			self.store.update_ep(ep)

		kube_list_obj(self.obj_api, RESOURCES.endpoints, list_endpoint_obj_fn)
		logger.debug("Bootstrap Endpoint store: ".format(self.store._dump_eps()))

	def on_endpoint_delete(self, body, spec, **kwargs):
		logger.info("on_endpoint_delete {}".format(spec))

	def on_endpoint_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_endpoint_provisioned {}".format(spec))
		ep = Endpoint(name, self.obj_api, self.store, spec)
		self.store.update_ep(ep)

	def on_bouncer_placed(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Endpoint on_bouncer_placed {}".format(spec))
		b = Bouncer(name, self.obj_api, None, spec)
		eps = self.store.get_eps_in_net(b.net)
		b.update_eps(eps)
		b.set_status(OBJ_STATUS.bouncer_status_endpoint_ready)
		b.update_obj()

	def on_bouncer_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Endpoint on_bouncer_provisioned {}".format(spec))
		b = Bouncer(name, self.obj_api, None, spec)
		eps = self.store.get_eps_in_net(b.net)
		for ep in eps:
			ep.update_bouncers(set([b]))

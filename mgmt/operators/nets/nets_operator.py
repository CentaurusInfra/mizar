import random
import logging
from kubernetes import client, config
from common.cidr import Cidr
from common.constants import *
from common.common import *
from obj.net import Net
from store.operator_store import OprStore

logger = logging.getLogger()

class NetOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(NetOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_startup(self, logger, **kwargs):
		def list_net_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped {}".format(name))
			n = Net(name, self.obj_api, self.store, spec)
			self.store.update_net(n)

		kube_list_obj(self.obj_api, RESOURCES.nets, list_net_obj_fn)
		self.create_default_net()
		logger.debug("Bootstrap Net store: ".format(self.store._dump_nets()))

	def create_default_net(self):
		if self.store.get_net(OBJ_DEFAULTS.default_ep_net):
			return
		n = Net(OBJ_DEFAULTS.default_ep_net, self.obj_api, self.store)
		n.create_obj()

	def on_net_init(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Net on_net_init {}".format(spec))
		n = Net(name, self.obj_api, self.store, spec)
		v = self.store.get_vpc(n.vpc)
		n.set_vni(v.vni)
		for i in range(n.n_bouncers):
			n.create_bouncer()
		n.set_status(OBJ_STATUS.net_status_allocated)
		n.update_obj()

	def on_net_delete(self, body, spec, **kwargs):
		logger.info("on_net_delete {}".format(spec))

	def on_bouncer_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Net on_bouncer_provisioned {} with spec: {}".format(name, spec))
		b = Bouncer(name, self.obj_api, None, spec)
		n = self.store.get_net(b.net)
		if n.status != OBJ_STATUS.net_status_provisioned:
			n.set_status(OBJ_STATUS.net_status_provisioned)
			n.update_obj()

	def on_endpoint_init(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Net on_endpoint_init {} with spec: {}".format(name, spec))
		ep = Endpoint(name, self.obj_api, None, spec)
		n = self.store.get_net(ep.net)
		ip = n.allocate_ip()
		ep.set_ip(ip)
		n.mark_ip_as_allocated(ip)
		ep.set_status(LAMBDAS.endpoint_status_allocated)
		ep.update_obj()

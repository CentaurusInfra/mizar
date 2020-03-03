import random
import uuid
import logging
from kubernetes import client, config
from common.constants import *
from common.common import *
from common.cidr import Cidr
from obj.vpc import Vpc
from obj.net import Net
from obj.divider import Divider
from store.operator_store import OprStore
logger = logging.getLogger()

class VpcOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(VpcOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_startup(self, logger, **kwargs):
		def list_vpc_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped {}".format(name))
			v = Vpc(name, self.obj_api, self.store, spec)
			if v.status == OBJ_STATUS.vpc_status_init:
				return self._on_vpc_init(name, spec)
			self.store.update_vpc(v)

		kube_list_obj(self.obj_api, RESOURCES.vpcs, list_vpc_obj_fn)
		self.create_default_vpc()
		logger.debug("Bootstrap VPC store: ".format(self.store._dump_vpcs()))

	def create_default_vpc(self):
		if self.store.get_vpc(OBJ_DEFAULTS.default_ep_vpc):
			return
		v = Vpc(OBJ_DEFAULTS.default_ep_vpc, self.obj_api, self.store)
		v.create_obj()

	def on_vpc_init(self, body, spec, **kwargs):
		name = kwargs['name']
		self._on_vpc_init(name, spec)

	def _on_vpc_init(self, name, spec):
		logger.info("on_vpc_init {} with spec: {}".format(name, spec))
		v = Vpc(name, self.obj_api, self.store, spec)
		v.set_vni(self.allocate_vni(v))
		for i in range(v.n_dividers):
			logger.info("Create divicer {} for vpc: {}".format(i, name))
			v.create_divider()
		v.set_status(OBJ_STATUS.vpc_status_allocated)
		v.update_obj()

	def on_divider_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_divider_provisioned {} with spec: {}".format(name, spec))
		div = Divider(name, self.obj_api, None, spec)
		v = self.store.get_vpc(div.vpc)
		if v.status != OBJ_STATUS.vpc_status_provisioned:
			v.set_status(OBJ_STATUS.vpc_status_provisioned)
			v.update_obj()

	def on_vpc_delete(self, body, spec, **kwargs):
		logger.info("on_vpc_delete {}".format(spec))

	def allocate_vni(self, vpc):
		# Scrappy allocator for now!!
		# TODO: There is a tiny chance of collision here, not to worry about now
		if vpc.name == OBJ_DEFAULTS.default_ep_vpc:
			return OBJ_DEFAULTS.default_vpc_vni
		return uuid.uuid4().int & (1<<24)-1


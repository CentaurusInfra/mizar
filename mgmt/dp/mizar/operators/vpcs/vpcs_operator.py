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

	def query_existing_vpcs(self):
		def list_vpc_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped {}".format(name))
			v = self.get_vpc_stored_obj(name, spec)
			if v.status == OBJ_STATUS.vpc_status_provisioned:
				self.store_update(v)

		kube_list_obj(self.obj_api, RESOURCES.vpcs, list_vpc_obj_fn)
		logger.debug("Bootstrap VPC store: ".format(self.store._dump_vpcs()))

	def get_vpc_tmp_obj(self, name, spec):
		return Vpc(name, self.obj_api, None, spec)

	def get_vpc_stored_obj(self, name, spec):
		return Vpc(name, self.obj_api, self.store, spec)

	def create_default_vpc(self):
		if self.store.get_vpc(OBJ_DEFAULTS.default_ep_vpc):
			return
		v = Vpc(OBJ_DEFAULTS.default_ep_vpc, self.obj_api, self.store)
		v.create_obj()

	def store_update(self, vpc):
		self.store.update_vpc(vpc)

	def create_vpc_dividers(self, vpc):
		for i in range(vpc.n_dividers):
			logger.info("Create divider {} for vpc: {}".format(i, vpc.name))
			vpc.create_divider()

	def set_vpc_provisioned(self, vpc):
		vpc.set_status(OBJ_STATUS.vpc_status_provisioned)
		vpc.update_obj()

	def on_divider_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		self._on_divider_provisioned(name, spec)

	def _on_divider_provisioned(self, name, spec):
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
		vpc.set_vni(uuid.uuid4().int & (1<<24)-1)


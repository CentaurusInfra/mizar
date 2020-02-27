import random
import uuid
from kubernetes import client, config
from common.constants import *
from common.common import *
from obj.vpc import Vpc
from store.operator_store import OprStore
from store.droplets_store import DropletStore
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
		self.ds = DropletStore()
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_startup(self, logger, **kwargs):
		logger.info("divider on_startup")

	def on_vpc_allocated(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Divider on_vpc_allocated {} with spec: {}".format(name, spec))
		v = Vpc(name, self.obj_api, self.store, spec)
		self.schedule_dividers(v)
		v.update_obj()

	def schedule_dividers(vpc):
		droplets = set(self.store.get_all_droplets())
		for i in vpc.n_dividers:
			j = random.choice(range(len(droplets)))
			d = droplets[j]
			droplets.remove(j)
			vpc.update_divider(d)

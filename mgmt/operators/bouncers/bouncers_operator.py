import random
from kubernetes import client, config
from obj.bouncer import Bouncer
from common.constants import *
from common.common import *
from obj.net import Net
from store.operator_store import OprStore
from store.droplets_store import DropletStore
import logging

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
		self.ds = DropletStore()
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_startup(self, logger, **kwargs):
		logger.info("bouncer on_startup")

	def on_net_allocated(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Bouncer on_net_allocated {} with spec: {}".format(name, spec))
		n = Net(name, self.obj_api, self.store, spec)
		self.schedule_bouncers(n)
		n.set_status(OBJ_STATUS.net_status_ready)
		n.update_obj()

	def schedule_bouncers(self, net):
		droplets = set(self.store.get_all_droplets())
		for i in range(net.n_bouncers):
			d = random.sample(droplets, 1)[0]
			net.update_bouncer(d)
			droplets.remove(d)

	def on_bouncer_init(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Bouncer on_bouncer_init {} with spec: {}".format(name, spec))
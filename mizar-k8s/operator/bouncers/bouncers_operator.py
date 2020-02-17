from vpcs.vpcs_store import VpcStore
from droplets.droplets_store import DropletStore
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
		self.vs = VpcStore()

	def on_delete(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("*delete_bouncer {}".format(name))

	def on_update(self, body, spec, **kwargs):
		name = kwargs['name']
		ip = spec['ip']
		logger.info("*update_bouncer {}, {}".format(name, ip))

	def on_create(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

	def on_resume(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

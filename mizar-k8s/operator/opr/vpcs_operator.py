from opr.droplet import VpcStore
import logging
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
		self.vs = VpcStore()

	def on_create(self, body, spec, **kwargs):
		logger.info("*create_vpc {}, {}".format(spec, kwargs))

	def on_delete(self, body, spec, **kwargs):
		logger.info("*delete_vpc {}, {}".format(spec, kwargs))

	def on_update(self, body, spec, **kwargs):
		logger.info("*update_vpc {}".format(kwargs))

	def on_resume(self, spec, **kwargs):
		logger.info("*resume_vpc {}".format(kwargs))

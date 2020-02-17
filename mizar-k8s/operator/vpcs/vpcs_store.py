import logging

logger = logging.getLogger()

class VpcStore(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(VpcStore, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = {}

	def update(self, name, vpc):
		self.store[name] = vpc

	def delete(self, name):
		if name in self.store:
			del self.store[name]

	def get(self, name):
		if name in self.store:
			return self.store[name]
		return None
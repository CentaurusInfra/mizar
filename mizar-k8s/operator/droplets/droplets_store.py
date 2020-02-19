import logging

logger = logging.getLogger()

class DropletStore(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(DropletStore, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = {}

	def update(self, name, droplet):
		self.store[name] = droplet

	def delete(self, name):
		if name in self.store:
			del self.store[name]

	def get(self, name):
		if name in self.store:
			return self.store[name]
		return None

	def get_all(self):
		return list(self.store.values())
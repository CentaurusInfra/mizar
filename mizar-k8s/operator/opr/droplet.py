import logging

logger = logging.getLogger()

class Droplet(object):
	def __init__(self, name, ip, mac):
		self.name = name
		self.ip = ip
		self.mac = mac

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

	def update(self, name, ip, mac):
		d = Droplet(name, ip, mac)
		self.store[name] = d

	def delete(self, name):
		if name in self.store:
			del self.store[name]

	def get(self, name):
		if name in self.store:
			return self.store[name]
		return None
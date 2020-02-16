import logging

logger = logging.getLogger()

class Vpc(object):
	def __init__(self, name, vni, cidr, dividers={}, networks={}):
		self.name = name
		self.vni = vni
		self.cidr = cidr
		self.dividers = dividers
		self.networks = networks

	def update_divider(self, droplet):
		pass

	def delete_divider(self, droplet):
		pass

	def update_network(self, network):
		pass

	def delete_network(self, network):
		pass

	def update_bouncer(self, network, bouncer):
		pass

	def delete_bouncer(self, network, bouncer):
		pass

	def update_simple_endpoint(self):
		pass

	def delete_simple_endpoint(self):
		pass

	def update_host_endpoint(self):
		pass

	def delete_host_endpoint(self):
		pass

	def update_scaled_endpoint(self):
		pass

	def delete_scaled_endpoint(self):
		pass


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

	def update(self, name, vni, cidr):
		v = Vpc(name, vni, cidr)
		self.store[name] = v

	def delete(self, name):
		if name in self.store:
			del self.store[name]

	def get(self, name):
		if name in self.store:
			return self.store[name]
		return None
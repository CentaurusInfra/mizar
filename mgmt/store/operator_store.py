import logging

logger = logging.getLogger()

class OprStore(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(OprStore, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.vpcs_store = {}
		self.nets_store = {}
		self.eps_store = {}
		self.dividers_store = {}
		self.droplets_store = {}

	def update_vpc(self,vpc):
		self.vpcs_store[vpc.name] = vpc

	def delete_vpc(self, name):
		if name in self.vpcs_store:
			del self.vpcs_store[name]

	def get_vpc(self, name):
		if name in self.vpcs_store:
			return self.vpcs_store[name]
		return None

	def contains_vpc(self, name):
		if name in self.vpcs_store:
			return True
		return False

	def _dump_vpcs(self):
		for v in self.vpcs_store.values():
			logger.info("VPC: {}, Spec: {}".format(v.name, v.get_obj_spec()))

	def update_net(self,net):
		self.nets_store[net.name] = net

	def delete_net(self, name):
		if name in self.nets_store:
			del self.nets_store[name]

	def get_net(self, name):
		if name in self.nets_store:
			return self.nets_store[name]
		return None

	def contains_net(self, name):
		if name in self.nets_store:
			return True
		return False

	def _dump_nets(self):
		for n in self.nets_store.values():
			logger.info("Net: {}, Spec: {}".format(n.name, n.get_obj_spec()))

	def update_ep(self,ep):
		self.eps_store[ep.name] = ep

	def delete_ep(self, name):
		if name in self.eps_store:
			del self.eps_store[name]

	def get_ep(self, name):
		if name in self.eps_store:
			return self.eps_store[name]
		return None

	def contains_ep(self, name):
		if name in self.eps_store:
			return True
		return False

	def _dump_eps(self):
		for e in self.eps_store.values():
			logger.info("EP: {}, Spec: {}".format(e.name, e.get_obj_spec()))

	def update_droplet(self,droplet):
		self.droplets_store[droplet.name] = droplet

	def delete_droplet(self, name):
		if name in self.droplets_store:
			del self.droplets_store[name]

	def get_droplet(self, name):
		if name in self.droplets_store:
			return self.droplets_store[name]
		return None

	def get_all_droplets(self):
		return self.droplets_store.values()

	def contains_droplet(self, name):
		if name in self.droplets_store:
			return True
		return False

	def _dump_droplets(self):
		for d in self.droplets_store.values():
			logger.info("Droplets: {}, Spec: {}".format(d.name, d.get_obj_spec()))

	def update_divider(self,div):
		self.dividers_store[div.name] = div

	def delete_divider(self, name):
		if name in self.dividers_store:
			del self.dividers_store[name]

	def get_divider(self, name):
		if name in self.dividers_store:
			return self.dividers_store[name]
		return None

	def contains_divider(self, name):
		if name in self.dividers_store:
			return True
		return False

	def _dump_dividers(self):
		for d in self.dividers_store.values():
			logger.info("EP: {}, Spec: {}".format(d.name, d.get_obj_spec()))
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
		self.droplets_store = {}

		self.vpcs_store = {}
		self.nets_store = {}

		self.eps_store = {}
		self.eps_net_store = {}

		self.dividers_store = {}
		self.dividers_vpc_store = {}

		self.bouncers_store = {}
		self.bouncers_net_store = {}
		self.bouncers_vpc_store = {}

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
		if ep.net not in self.eps_net_store:
			self.eps_net_store[ep.net] = set()
		self.eps_net_store[ep.net].add(ep)

	def delete_ep(self, name):
		if name not in self.eps_store:
			return
		ep = self.eps_store[name]

		self.eps_net_store[ep.net].remove(name)
		del self.eps_store[name]
		l = len(self.eps_net_store[ep.net])
		if  l == 0:
			del self.eps_net_store[ep.net]

	def get_ep(self, name):
		if name in self.eps_store:
			return self.eps_store[name]
		return None

	def get_eps_in_net(self, net):
		if net in self.eps_net_store:
			return self.eps_net_store[net]
		return set()

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

		if div.vpc not in self.dividers_store:
			self.dividers_vpc_store[div.vpc] = set()
		self.dividers_vpc_store[div.vpc].add(div)

	def delete_divider(self, name):
		if name not in self.dividers_store:
			return
		d = self.dividers_store[name]

		self.dividers_vpc_store[d.vpc].remove(d)
		del self.dividers_store[name]

		l = len(self.dividers_vpc_store[d.vpc])
		if  l == 0:
			del self.dividers_vpc_store[d.vpc]


	def get_divider(self, name):
		if name in self.dividers_store:
			return self.dividers_store[name]
		return None

	def get_dividers_of_vpc(self, vpc):
		if vpc in self.dividers_vpc_store:
			return self.dividers_vpc_store[vpc]
		return set()

	def contains_divider(self, name):
		if name in self.dividers_store:
			return True
		return False

	def _dump_dividers(self):
		for d in self.dividers_store.values():
			logger.info("EP: {}, Spec: {}".format(d.name, d.get_obj_spec()))


	def update_bouncer(self, b):
		self.bouncers_store[b.name] = b

		if b.net not in self.bouncers_net_store:
			self.bouncers_net_store[b.net] = set()
		self.bouncers_net_store[b.net].add(b)

		if b.vpc not in self.bouncers_vpc_store:
			self.bouncers_vpc_store[b.vpc] = set()
		self.bouncers_vpc_store[b.vpc].add(b)

	def delete_bouncer(self, name):
		if name not in self.bouncers_store:
			return
		b = self.bouncers_store[name]

		self.bouncers_net_store[b.net].remove(b)
		self.bouncers_vpc_store[b.vpc].remove(b)
		del self.bouncers_store[name]

		l = len(self.bouncers_net_store[b.net])
		if  l == 0:
			del self.bouncers_net_store[b.net]

		l = len(self.bouncers_vpc_store[b.vpc])
		if  l == 0:
			del self.bouncers_vpc_store[b.vpc]

	def get_bouncer(self, name):
		if name in self.bouncers_store:
			return self.bouncers_store[name]
		return None

	def get_bouncers_of_net(self, net):
		if net in self.bouncers_net_store:
			return self.bouncers_net_store[net]
		return set()

	def get_bouncers_of_vpc(self, vpc):
		if vpc in self.bouncers_vpc_store:
			return self.bouncers_vpc_store[vpc]
		return set()

	def contains_bouncer(self, name):
		if name in self.bouncers_store:
			return True
		return False

	def _dump_bouncers(self):
		for b in self.bouncers_store.values():
			logger.info("Bouncer: {}, Spec: {}".format(b.name, b.get_obj_spec()))
import logging

logger = logging.getLogger()

class Net(object):
	def __init__(self, name, vpc, vni, cidr, bouncers={}, endpoints={}):
		self.name = name
		self.vpc = vpc
		self.vni = vni
		self.cidr = cidr
		self.bouncers = bouncers
		self.endpoints = endpoints

	def update_bouncer(self, network, bouncer):
		pass

	def delete_bouncer(self, network, bouncer):
		pass

	def update_gw_endpoint(self):
		pass

	def delete_gw_endpoint(self):
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
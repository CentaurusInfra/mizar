import logging

logger = logging.getLogger()

class Bouncer(object):
	def __init__(self, name, vpc, net, ip, droplet, droplet_obj):
		self.name = name
		self.droplet = droplet
		self.vpc = vpc
		self.net = net
		self.ip = ip
		self.mac = ""
		self.droplet_obj = droplet_obj

	def get_obj_spec(self):
		self.obj = {
			"vpc": self.vpc,
			"net": self.net,
			"ip": self.ip,
			"mac": self.mac,
			"status": self.status,
			"droplet": self.droplet
		}

		return self.obj

	def create_obj(self):
		pass

	def update_obj(self):
		pass

	def delete_obj(self):
		pass

	def watch_obj(self):
		pass

	def update_simple_endpoint(self, ep):
		logger.info("Bouncer {} update_simple_endpoint {} on droplet {}".format(self.name, ep.name, ep.droplet))
		self.droplet_obj.update_ep(ep)
		self.droplet_obj.update_substrate_ep(ep.droplet_obj)

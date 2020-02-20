import logging

logger = logging.getLogger()

class Bouncer(object):
	def __init__(self, name, vpc, net, ip, droplet):
		self.name = name
		self.droplet = droplet
		self.vpc = vpc
		self.net = net
		self.ip = ip

	def update_simple_endpoint(self, ep):
		logger.info("Bouncer {} update_simple_endpoint {}".format(self.name, ep.name))
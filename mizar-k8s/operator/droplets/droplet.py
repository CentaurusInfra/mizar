import logging

logger = logging.getLogger()

class Droplet(object):
	def __init__(self, name, ip, mac):
		self.name = name
		self.ip = ip
		self.mac = mac
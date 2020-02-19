import logging

logger = logging.getLogger()

class Bouncer(object):
	def __init__(self, name, droplet):
		self.name = name
		self.droplet = Droplet
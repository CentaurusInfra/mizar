import logging

logger = logging.getLogger()

class Divider(object):
	def __init__(self, name, droplet):
		self.name = name
		self.droplet = Droplet
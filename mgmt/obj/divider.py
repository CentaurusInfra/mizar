import logging

logger = logging.getLogger()

class Divider(object):
	def __init__(self, name, droplet):
		self.name = name
		self.vpc = ""
		self.ip = ""
		self.mac = ""
		self.droplet = Droplet
		self.status = ""

	def get_obj_spec(self):
		self.obj = {
			"vpc": self.vpc,
			"mac": self.mac,
			"ip": self.ip,
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

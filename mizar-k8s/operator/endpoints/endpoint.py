


class Endpoint:
	def __init__(self, name, vpc, net, vni, status, gw, ip, mac, ep_type, obj_api):
		self.name = name
		self.obj_api = obj_api
		self.vpc = vpc
		self.net = net
		self.vni = vni
		self.status = status
		self.gw = gw
		self.ip = ip
		self.mac = mac
		self.type = ep_type

	def get_obj_spec(self):
		self.obj = {
				"type": self.type,
				"status": self.status,
				"vpc": self.vpc,
				"net": self.net,
				"ip": self.ip,
				"gw": self.gw,
				"mac": self.mac,
				"vni": self.vni
		}

		return self.obj
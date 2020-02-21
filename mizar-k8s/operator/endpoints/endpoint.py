from common.constants import *

class Endpoint:
	def __init__(self, name, droplet, droplet_obj, vpc, net, vni, status, gw, ip, mac, ep_type, obj_api):
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
		self.droplet = droplet
		self.droplet_obj = droplet_obj
		self.veth_peer = ""
		self.veth_name = ""

	def get_obj_spec(self):
		self.obj = {
				"type": self.type,
				"status": self.status,
				"vpc": self.vpc,
				"net": self.net,
				"ip": self.ip,
				"gw": self.gw,
				"mac": self.mac,
				"vni": self.vni,
				"droplet": self.droplet
		}

		return self.obj

	def get_veth_peer(self):
		return self.veth_peer

	def get_veth_name(self):
		return self.veth_name

	def get_tunnel_id(self):
		return str(self.vni)

	def get_ip(self):
		return str(self.ip)

	def get_eptype(self):
		if self.type == ep_type_simple:
			return str(CONSTANTS.TRAN_SIMPLE_EP)

	def get_mac(self):
		return str(self.mac)

	def get_remote_ips(self):
		remote_ips = []
		remote_ips = self.droplet_obj and [str(self.droplet_obj.ip)]
		return remote_ips
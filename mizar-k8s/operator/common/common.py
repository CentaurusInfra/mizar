from netaddr import *

class Cidr:
	def __init__(self, prefixlen, ip):
		"""
		Defines an IPv4 CIDR block
		"""
		self.prefixlen = prefixlen
		self.ip = ip
		self.ipnet = IPNetwork("{}/{}".format(self.ip, self.prefixlen))

	def get_ip(self, idx):
		return self.ipnet[idx]
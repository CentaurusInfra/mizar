import ipaddress

class Cidr:
	def __init__(self, prefixlen, ip):
		"""
		Defines an IPv4 CIDR block
		"""
		self.prefixlen = prefixlen
		self.ip = ip
		self.ipnet = ipaddress.ip_network("{}/{}".format(self.ip, self.prefixlen))
		self.subnets = self.ipnet.subnets(new_prefix=29)

		self.pool = None
		self._hosts = set()
		self.gw = self.get_ip(1)
		self.allocated = set()

	@property
	def hosts(self):

		self.pool = next(self.subnets)
		self._hosts.update(set(self.pool.hosts()))
		self._hosts.discard(self.gw)
		return self._hosts

	def get_ip(self, idx):
		return self.ipnet[idx]

	def get_hosts(self):
		return self.hosts

	def allocate_ip(self):
		if not len(self.hosts):
			return None
		ip = self.hosts.pop()
		# TODO: bad hack, search the list and remove it!!
		while ip in self.allocated:
			ip = self.hosts.pop()
		self.allocated.add(ip)
		return str(ip)

	def mark_ip_as_allocated(self, ip):
		self.allocated.add(ipaddress.IPv4Address(ip))

	def deallocate_ip(self, ip):
		ip = ipaddress.IPv4Address(ip)
		if ip in self.hosts:
			if ip in self.allocated:
				self.allocated.remove(ip)
			ip = self._hosts.add(ip)


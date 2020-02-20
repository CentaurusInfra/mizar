import logging
import random
from kubernetes.client.rest import ApiException

logger = logging.getLogger()

class Vpc(object):
	def __init__(self, obj_api, name, vni, cidr, dividers={}, networks={}):
		self.name = name
		self.vni = vni
		self.cidr = cidr
		self.dividers = dividers
		self.networks = networks
		self.obj_api = obj_api
		self.obj = None
		h = '{:06x}'.format(int(self.vni))
		self.vni_mac = '{}:{}:{}'.format(h[0:2], h[2:4], h[4:6])
		self.allocated_mac = set()
		#TODO What if the vni is > 24bits (we have it 64)
		#by default?

	def get_obj_spec(self):
		self.obj = {
			"ip": self.cidr.ip,
			"prefix": self.cidr.prefixlen,
			"vni": self.vni,
			"dividers": len(self.dividers.keys()),
		}

		return self.obj

	def update_divider(self, droplet):
		logger.info("*Update dividers {}".format(droplet.name))
		if droplet.name in self.dividers:
			return True

		self.dividers[droplet.name] = droplet

		divider_name = self.name +'-divider-' + droplet.name

		try:

			api_response = self.obj_api.get_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural="dividers",
				name=divider_name)
			logger.info("Exist {}".format(api_response))

		except ApiException as e:
			if e.status == 404:
				divider_obj = {
					"apiVersion": "mizar.com/v1",
					"kind": "Divider",
					"metadata": {
						"name": divider_name
					},
					"spec": {
						"ip": droplet.ip,
						"droplet": droplet.name,
						"vpc": self.name
					}
				}

				# create the divider resource
				self.obj_api.create_namespaced_custom_object(
					group="mizar.com",
					version="v1",
					namespace="default",
					plural="dividers",
					body=divider_obj,
				)
				return True

		return False

	def allocate_mac_address(self):
		trials = 0
		mac = "{}:{}:{}:{}".format(self.vni_mac,
				random.randint(0, 255),
				random.randint(0, 255),
				random.randint(0, 255))
		while mac in self.allocated_mac:
			mac = "{}:{}:{}:{}".format(self.vni_mac,
				random.randint(0, 255),
				random.randint(0, 255),
				random.randint(0, 255))
			trials += 1
			if trials == 1000:
				return None
		self.allocated_mac.add(mac)
		return mac

	def mark_mac_address_as_allocated(self, mac):
		self.allocated_mac.add(mac)

	def deallocate_mac_address(self, mac):
		self.allocated_mac.remove(mac)

	def delete_divider(self, droplet):
		pass

	def get_network(self, name):
		if name in self.networks:
			return self.networks[name]
		return None

	def update_network(self, name, network):
		self.networks[name]=network
		logger.info("networks {}".format(self.networks.keys()))

	def delete_network(self, network):
		pass

	def update_bouncer(self, network, bouncer):
		pass

	def delete_bouncer(self, network, bouncer):
		pass

	def update_simple_endpoint(self, ep):
		logger.info("update_simple_endpoint of vpc {}".format(self.name))
		pass

	def delete_simple_endpoint(self):
		pass

	def update_host_endpoint(self):
		pass

	def delete_host_endpoint(self):
		pass

	def update_scaled_endpoint(self):
		pass

	def delete_scaled_endpoint(self):
		pass

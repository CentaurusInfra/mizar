import logging
from kubernetes.client.rest import ApiException

logger = logging.getLogger()

class Net(object):
	def __init__(self, obj_api, name, vpc, vni, cidr, bouncers={}, endpoints={}):
		self.name = name
		self.vpc = vpc
		self.vni = vni
		self.cidr = cidr
		self.bouncers = bouncers
		self.endpoints = endpoints
		self.obj_api = obj_api

	def get_obj_spec(self):
		self.obj = {
			"ip": self.cidr.ip,
			"prefix": self.cidr.prefixlen,
			"vni": self.vni,
			"vpc": self.vpc,
			"bouncers": len(self.bouncers.keys()),
		}

		return self.obj

	def update_bouncer(self, droplet):
		logger.info("*Update bouncer {}".format(droplet.name))
		if droplet.name in self.bouncers:
			return True

		self.bouncers[droplet.name] = droplet

		bouncer_name = self.name +'-bouncer-' + droplet.name
		try:

			api_response = self.obj_api.get_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural="bouncers",
				name=bouncer_name)
			logger.info("Exist {}".format(api_response))

		except ApiException as e:
			logger.info("Get {}".format(bouncer_name))
			logger.info("Except {}".format(e.status))

			bouncer_obj = {
				"apiVersion": "mizar.com/v1",
				"kind": "Bouncer",
				"metadata": {
					"name": bouncer_name
				},
				"spec": {
					"ip": droplet.ip,
					"droplet": droplet.name,
					"vpc": self.name
				}
			}

			# create the bouncer resource
			self.obj_api.create_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural="bouncers",
				body=bouncer_obj,
			)
			return True

		return False

	def delete_bouncer(self, network, bouncer):
		pass

	def update_gw_endpoint(self):
		pass

	def delete_gw_endpoint(self):
		pass

	def update_simple_endpoint(self):
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
import logging
from common.constants import *
from kubernetes.client.rest import ApiException

logger = logging.getLogger()

class Net(object):
	def __init__(self, obj_api, name, vpc, vni, cidr):
		self.name = name
		self.vpc = vpc
		self.vni = vni
		self.cidr = cidr
		self.bouncers = {}
		self.endpoints = {}
		self.obj_api = obj_api
		self.gw = self.cidr.gw

	def get_obj_spec(self):
		self.obj = {
			"ip": self.cidr.ip,
			"prefix": self.cidr.prefixlen,
			"vni": self.vni,
			"vpc": self.vpc,
			"bouncers": len(self.bouncers.keys()),
		}

		return self.obj

	def update_bouncer(self, bouncer):
		logger.info("*Update bouncer {}, {}, {}".format(bouncer.name, bouncer.vpc, bouncer.net))
		logger.info("*Update bouncer - net {}, {}, {}".format(self.vpc, self.name, self.bouncers.keys()))
		self.bouncers[bouncer.name] = bouncer
		# TODO: This is a new bouncer, program it with existing endpoints and update the transit agentmetadata

	def create_bouncer(self, droplet):
		logger.info("*Create bouncer {}".format(droplet.name))

		bouncer_name = self.name +'-bouncer-' + droplet.name
		if bouncer_name in self.bouncers:
			return True
		try:

			api_response = self.obj_api.get_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural="bouncers",
				name=bouncer_name)
			logger.info("Exist {}".format(api_response))

		except:
			logger.info("Get {}".format(bouncer_name))

			bouncer_obj = {
				"apiVersion": "mizar.com/v1",
				"kind": "Bouncer",
				"metadata": {
					"name": bouncer_name
				},
				"spec": {
					"ip": droplet.ip,
					"droplet": droplet.name,
					"vpc": self.vpc,
					"net": self.name
				}
			}
			logger.info("### Bouncer obj {}".format(bouncer_obj))
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

	def allocate_ip(self):
		return self.cidr.allocate_ip()

	def deallocate_ip(self, ip):
		return self.cidr.deallocate_ip(ip)

	def mark_ip_as_allocated(self, ip):
		self.cidr.mark_ip_as_allocated(ip)

	def delete_bouncer(self, network, bouncer):
		pass

	def update_gw_endpoint(self):
		pass

	def delete_gw_endpoint(self):
		pass

	def update_simple_endpoint(self, ep):
		if ep.status != ep_status_allocated:
			logger.info("Nothing to do for the endpoint {} , status must be allocated!".format(self.name))
			return
		logger.info("update_simple_endpoint {} of net {} bouncers {}".format(ep.name, self.name, self.bouncers.keys()))
		self.endpoints[ep.name] = ep
		bouncers = self.bouncers.values()
		for b in bouncers:
			b.update_simple_endpoint(ep)


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
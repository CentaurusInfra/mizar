import logging
from kubernetes import client, config

logger = logging.getLogger()

class MizarApi:

	def __init__(self):
		config.load_kube_config()
		self.obj_api = client.CustomObjectsApi()

	def create_vpc(self, name, ip, prefix, dividers=1, vni=None):
		logger.info("Creating a vpc!!!")
		spec = {
			"ip": ip,
			"prefix": prefix,
			"vni": vni,
			"dividers": dividers,
		}
		self.create_obj(name, "Vpc", spec, "vpcs")

		logger.debug("Created {} {}".format("Vpc", name))

	def delete_vpc(self, name):
		logger.info("Delete a vpc!!!")
		self.delete_obj(name, "vpcs")


	def create_net(self):
		pass

	def delete_net(self):
		pass

	def create_obj(self, name, kind, spec, plural):
		spec["status"] = "Init"
		body = {
			"apiVersion": "mizar.com/v1",
			"kind": kind,
			"metadata": {
				"name": name
			},
			"spec": spec
		}
		self.obj_api.create_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural= plural,
			body=body,
		)

	def delete_obj(self, name, plural):
		self.obj_api.delete_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural=plural,
			name=name,
			body=client.V1DeleteOptions(),
			propagation_policy="Orphan")
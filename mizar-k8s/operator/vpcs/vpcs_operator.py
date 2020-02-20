import random
from kubernetes import client, config
from common.common import Cidr
from vpcs.vpc import Vpc
from vpcs.vpcs_store import VpcStore
from droplets.droplets_store import DropletStore
import logging
logger = logging.getLogger()

class VpcOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(VpcOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.ds = DropletStore()
		self.vs = VpcStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()
		self.query_existing_vpcs(self)

	def query_existing_vpcs(self):
		logger.info("* query vpcs")
		response = self.obj_api.list_namespaced_custom_object(
						group = "mizar.com",
						version = "v1",
						namespace = "default",
						plural = "vpcs",
						watch=False)
		items = response['items']
		for v in items:
			name = v['metadata']['name']
			vni = v['spec']['vni']
			ip = v['spec']['ip']
			prefix = v['spec']['prefix']
			dividers =  v['spec']['dividers']
			cidr = Cidr(prefix, ip)
			vpc = self.vs.get(name)
			if vpc is None:
				vpc = Vpc(self.obj_api, name, vni, cidr)
			self.vs.update(name, vpc)


	def on_update(self, body, spec, **kwargs):
		update_object = False

		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		dividers = 1

		if 'dividers' in spec:
			dividers = spec['dividers']
		else:
			update_object = True

		cidr = Cidr(prefix, ip)
		logger.info("*update_vpc name: {}, vni: {}, ip: {}/{}".format(name, vni, ip, prefix))

		vpc = self.vs.get(name)
		if vpc is None:
			vpc = Vpc(self.obj_api, name, vni, cidr)

		# First allocate the divider if it does not exist
		# TODO: This code just allocate ONE divider, no support
		# For scaling yet!!
		self.allocate_divider(vpc)

		self.vs.update(name, vpc)

		# If we have change in the object field, update it
		if update_object:
			logger.info("Update vpc fields")
			self.update_vpc(vpc, body)

	def on_create(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

	def on_resume(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

	def on_delete(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("*delete_vpc name: {}".format(name))

	def allocate_divider(self, vpc):
		# Simple random allocator for now
		droplets = self.ds.get_all()
		if droplets is None:
			return False
		logger.info("droplets {}".format(droplets))
		divider = random.choice(droplets)
		vpc.update_divider(divider)
		return True


	def update_vpc(self, vpc, body):
		# update the resource
		body['spec'] = vpc.get_obj_spec()
		self.obj_api.patch_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="vpcs",
			name=vpc.name,
			body=body
		)

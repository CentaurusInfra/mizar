import random
import uuid
from kubernetes import client, config
from common.constants import *
from common.common import *
from common.cidr import Cidr
from obj.vpc import Vpc
from obj.net import Net
from store.operator_store import OprStore
from store.droplets_store import DropletStore
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
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_startup(self, logger, **kwargs):
		def list_vpc_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped {}".format(name))
			v = Vpc(name, self.obj_api, self.store, spec)
			self.store.update_vpc(v)

		kube_list_obj(self.obj_api, RESOURCES.vpcs, list_vpc_obj_fn)
		self.create_default_vpc()
		self.create_default_net()
		logger.debug("Bootstrap VPC store: ".format(self.store._dump_vpcs()))
		logger.debug("Bootstrap Net store: ".format(self.store._dump_nets()))

	def create_default_vpc(self):
		v = Vpc(OBJ_DEFAULTS.default_ep_vpc, self.obj_api, self.store)
		v.create_obj()

	def create_default_net(self):
		n = Net(OBJ_DEFAULTS.default_ep_net, self.obj_api, self.store)
		n.create_obj()

	def on_vpc_init(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("on_vpc_init {} with spec: {}".format(name, spec))
		v = Vpc(name, self.obj_api, self.store, spec)
		v.set_vni(self.allocate_vni(v))
		v.set_status(OBJ_STATUS.vpc_status_allocated)
		v.update_obj()

	def on_vpc_ready(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Vpc on_vpc_ready {} with spec: {}".format(name, spec))
		v = Vpc(name, self.obj_api, self.store, spec)
		v.set_status(OBJ_STATUS.vpc_status_provisioned)
		v.update_obj()

	def on_vpc_delete(self, body, spec, **kwargs):
		logger.info("on_vpc_delete {}".format(spec))

	def allocate_vni(self, vpc):
		# Scrappy allocator for now!!
		# TODO: There is a tiny chance of collision here, not to worry about now
		if vpc.name == OBJ_DEFAULTS.default_ep_vpc:
			return OBJ_DEFAULTS.default_vpc_vni
		return uuid.uuid4().int & (1<<24)-1


###

	# def query_existing_vpcs(self):
	# 	logger.info("* query vpcs")
	# 	response = self.obj_api.list_namespaced_custom_object(
	# 					group = "mizar.com",
	# 					version = "v1",
	# 					namespace = "default",
	# 					plural = "vpcs",
	# 					watch=False)
	# 	items = response['items']
	# 	for v in items:
	# 		name = v['metadata']['name']
	# 		vni = v['spec']['vni']
	# 		ip = v['spec']['ip']
	# 		prefix = v['spec']['prefix']
	# 		dividers =  v['spec']['dividers']
	# 		cidr = Cidr(prefix, ip)
	# 		vpc = self.vs.get(name)
	# 		if vpc is None:
	# 			vpc = Vpc(self.obj_api, name, vni, cidr)
	# 		self.vs.update(name, vpc)


	# def on_update(self, body, spec, **kwargs):
	# 	update_object = False

	# 	name = kwargs['name']
	# 	vni = spec['vni']
	# 	ip = spec['ip']
	# 	prefix = spec['prefix']
	# 	dividers = 1

	# 	if 'dividers' in spec:
	# 		dividers = spec['dividers']
	# 	else:
	# 		update_object = True

	# 	cidr = Cidr(prefix, ip)
	# 	logger.info("*update_vpc name: {}, vni: {}, ip: {}/{}".format(name, vni, ip, prefix))

	# 	vpc = self.vs.get(name)
	# 	if vpc is None:
	# 		vpc = Vpc(self.obj_api, name, vni, cidr)

	# 	# First allocate the divider if it does not exist
	# 	# TODO: This code just allocate ONE divider, no support
	# 	# For scaling yet!!
	# 	self.allocate_divider(vpc)

	# 	self.vs.update(name, vpc)

	# 	# If we have change in the object field, update it
	# 	if update_object:
	# 		logger.info("Update vpc fields")
	# 		self.update_vpc(vpc, body)

	# def on_create(self, body, spec, **kwargs):
	# 	self.on_update(body, spec, **kwargs)

	# def on_resume(self, body, spec, **kwargs):
	# 	self.on_update(body, spec, **kwargs)

	# def on_delete(self, body, spec, **kwargs):
	# 	name = kwargs['name']
	# 	logger.info("*delete_vpc name: {}".format(name))

	# def allocate_divider(self, vpc):
	# 	# Simple random allocator for now
	# 	droplets = self.ds.get_all()
	# 	if droplets is None:
	# 		return False
	# 	logger.info("droplets {}".format(droplets))
	# 	divider = random.choice(droplets)
	# 	vpc.update_divider(divider)
	# 	return True


	# def update_vpc(self, vpc, body):
	# 	# update the resource
	# 	body['spec'] = vpc.get_obj_spec()
	# 	self.obj_api.patch_namespaced_custom_object(
	# 		group="mizar.com",
	# 		version="v1",
	# 		namespace="default",
	# 		plural="vpcs",
	# 		name=vpc.name,
	# 		body=body
	# 	)

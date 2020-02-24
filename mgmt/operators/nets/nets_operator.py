import random
from kubernetes import client, config
from common.cidr import Cidr
from obj.net import Net
from store.vpcs_store import VpcStore
from store.droplets_store import DropletStore
import logging
logger = logging.getLogger()

class NetOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(NetOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.ds = DropletStore()
		self.vs = VpcStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()
		self.query_existing_nets(self)

	def query_existing_nets(self):
		logger.info("* query nets")
		response = self.obj_api.list_namespaced_custom_object(
						group = "mizar.com",
						version = "v1",
						namespace = "default",
						plural = "nets",
						watch=False)
		items = response['items']
		logger.info("net response {}".format(response))
		for v in items:
			name = v['metadata']['name']
			vni = v['spec']['vni']
			ip = v['spec']['ip']
			prefix = v['spec']['prefix']
			bouncers = 0
			if 'bouncers' in v['spec']:
				bouncers =  v['spec']['bouncers']
			vpc = v['spec']['vpc']
			cidr = Cidr(prefix, ip)
			net = self.vs.get(vpc).get_network(name)
			if net is None:
				net = Net(self.obj_api, name, vpc, vni, cidr)
			logger.info("* update nets {}".format(name))
			self.vs.get(vpc).update_network(name, net)

	def on_update(self, body, spec, **kwargs):
		update_object = False
		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		vpc = spec['vpc']
		cidr = Cidr(prefix, ip)

		bouncers = 1

		if 'bouncers' in spec:
			bouncers = spec['bouncers']
		else:
			update_object = True

		net = self.vs.get(vpc).get_network(name)
		if net is None:
			net = Net(self.obj_api, name, vpc, vni, cidr)


		# First allocate the bouncer if it does not exist
		# TODO: This code just allocate ONE bouncer, no support
		# For scaling yet!!
		self.allocate_bouncer(net)

		logger.info("*update_net name: {}, vni: {}, ip: {}/{}, vpc: {}".format(name, vni, ip, prefix, vpc))
		self.vs.get(vpc).update_network(name, net)

		# If we have change in the object field, update it
		if update_object:
			logger.info("Update net fields")
			self.update_net(net, body)

	def on_create(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

	def on_resume(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

	def on_delete(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("*delete_net name: {}".format(kwargs))

	def allocate_bouncer(self, net):
		# Simple random allocator for now
		droplets = self.ds.get_all()
		if droplets is None:
			return False
		logger.info("net droplets {}".format(droplets))
		bouncer = random.choice(droplets)
		net.create_bouncer(bouncer)
		return True

	def update_net(self, net, body):
		# update the resource
		body['spec'] = net.get_obj_spec()
		self.obj_api.patch_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="nets",
			name=net.name,
			body=body
		)
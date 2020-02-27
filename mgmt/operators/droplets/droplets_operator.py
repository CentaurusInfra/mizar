from common.constants import *
from common.common import *
from kubernetes import client, config
from obj.droplet import Droplet
from store.operator_store import OprStore
from store.droplets_store import DropletStore
import logging

logger = logging.getLogger()

class DropletOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(DropletOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.ds = DropletStore()
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_startup(self, logger, **kwargs):
		def list_doplet_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped droplet {}".format(name))
			d = Droplet(name, self.obj_api, self.store, spec)
			self.store.update_droplet(d)

		kube_list_obj(self.obj_api, RESOURCES.droplets, list_doplet_obj_fn)

	def on_droplet_init(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Droplet on_droplet_any {} with spec: {}".format(name, spec))
		d = Droplet(name, self.obj_api, self.store, spec)
		d.set_status(OBJ_STATUS.droplet_status_provisioned)
		d.update_obj()

	def on_droplet_provisioned(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("Droplet on_droplet_provisioned {} with spec: {}".format(name, spec))
		d = Droplet(name, self.obj_api, self.store, spec)
		self.store.update_droplet(d)

	def query_existing_droplets(self):
		logger.info("*query droplets")
		response = self.obj_api.list_namespaced_custom_object(
						group = "mizar.com",
						version = "v1",
						namespace = "default",
						plural = "droplets",
						watch=False)
		items = response['items']
		for v in items:
			name = v['metadata']['name']
			mac = v['spec']['mac']
			ip = v['spec']['ip']
			d = Droplet(name, ip, mac)
			self.ds.update(name, d)

	def on_delete(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("*delete_droplet {}".format(name))
		self.ds.delete(name)

	def on_update(self, body, spec, **kwargs):
		name = kwargs['name']
		mac = spec['mac']
		ip = spec['ip']
		logger.info("*update_droplet {}, {}, {}".format(name, ip, mac))
		d = Droplet(name, ip, mac)
		self.ds.update(name, d)


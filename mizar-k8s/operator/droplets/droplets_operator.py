from kubernetes import client, config
from droplets.droplet import Droplet
from droplets.droplets_store import DropletStore
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
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()
		self.query_existing_droplets(self)

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

	def on_create(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

	def on_resume(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)


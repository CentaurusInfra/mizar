from vpcs.vpcs_store import VpcStore
from droplets.droplets_store import DropletStore
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
		self.vs = VpcStore()

	def on_create(self, body, spec, **kwargs):
		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		vpc = spec['vpc']
		cidr = ''
		logger.info("*create_net name: {}, vni: {}, ip: {}/{}, vpc:{}".format(name, vni, ip, prefix, vpc))
		logger.info("vpc store {}".format(self.vs.store.keys()))
		self.vs.get(vpc).update_network("network-1")

	def on_delete(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("*delete_net name: {}".format(kwargs))

	def on_update(self, body, spec, **kwargs):
		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		vpc = spec['vpc']
		cidr = ''
		logger.info("*update_net name: {}, vni: {}, ip: {}/{}, vpc: {}".format(name, vni, ip, prefix, vpc))
		self.vs.get(vpc).update_network("network-1")

	def on_resume(self, spec, **kwargs):
		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		vpc = spec['vpc']
		cidr = ''
		logger.info("*resume_net name: {}, vni: {}, ip: {}/{}, vpc: {}".format(name, vni, ip, prefix, vpc))
		self.vs.get(vpc).update_network("network-1")

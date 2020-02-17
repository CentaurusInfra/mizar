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
		self.vs = VpcStore()

	def on_create(self, body, spec, **kwargs):
		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		cidr = ''
		logger.info("*create_vpc name: {}, vni: {}, ip: {}/{}".format(name, vni, ip, prefix))
		vpc = Vpc(name, vni, cidr)
		self.vs.update(name, vpc)

	def on_delete(self, body, spec, **kwargs):
		name = kwargs['name']
		logger.info("*delete_vpc name: {}".format(name))

	def on_update(self, body, spec, **kwargs):
		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		cidr = ''
		logger.info("*update_vpc name: {}, vni: {}, ip: {}/{}".format(name, vni, ip, prefix))
		vpc = Vpc(name, vni, cidr)
		self.vs.update(name, vpc)

	def on_resume(self, spec, **kwargs):
		name = kwargs['name']
		vni = spec['vni']
		ip = spec['ip']
		prefix = spec['prefix']
		cidr = ''
		logger.info("*resume_vpc name: {}, vni: {}, ip: {}/{}".format(name, vni, ip, prefix))
		vpc = Vpc(name, vni, cidr)
		self.vs.update(name, vpc)

from kubernetes import client, config
from obj.endpoint import Endpoint
from common.constants import *
from store.vpcs_store import VpcStore
from store.droplets_store import DropletStore
import logging
logger = logging.getLogger()

class EndpointOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(EndpointOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.ds = DropletStore()
		self.vs = VpcStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def on_delete(self, body, spec, **kwargs):
		logger.info("*delete_endpoint {}".format(self.ds.store))

	def on_update(self, body, spec, **kwargs):
		logger.info("*update_endpoint {}".format(body))
		update_endpoint = False

		name = kwargs['name']
		droplet = None
		droplet_obj = None
		if 'droplet' in spec:
			droplet = spec['droplet']
			droplet_obj = self.ds.get(droplet)

		vpc = default_ep_vpc
		if 'vpc' in spec:
			vpc = spec['vpc']

		net = default_ep_net
		if 'net' in spec:
			net = spec['net']

		ep_type = default_ep_type
		if 'type' in spec:
			ep_type = spec['type']

		vni = default_vpc_vni
		if 'vni' in spec:
			vni = spec['vni']
		else:
			#TODO validate than vni is the vni of the
			# given vpc
			pass

		itf = None
		if 'itf' in spec:
			itf = spec['itf']

		veth = None
		if 'veth' in spec:
			veth = spec['veth']

		netns = None
		if 'netns' in spec:
			netns = spec['netns']

		vpc_obj = self.vs.get(vpc)
		net_obj = vpc_obj.get_network(net)
		logger.info("got network {}".format(net))
		logger.info("have networks {}".format(vpc_obj.networks.keys()))
		# Get the GW from spec or network object
		gw = None
		if 'gw' in spec:
			gw = spec['gw']

		if gw == None:
			gw = str(net_obj.gw)
			update_endpoint = True

		prefix = None
		if 'prefix' in spec:
			prefix = spec['prefix']

		if prefix == None:
			prefix = str(net_obj.cidr.prefixlen)
			update_endpoint = True

		# Get or allocate the IP
		ip = None
		if 'ip' in spec:
			ip = spec['ip']

		if ip is None or ip == 'None':
			ip = str(net_obj.allocate_ip())
			update_endpoint = True
		else:
			net_obj.mark_ip_as_allocated(ip)

		mac = None
		if 'mac' in spec:
			mac = spec['mac']

		if mac is None:
			mac = vpc_obj.allocate_mac_address()
			update_endpoint = True
		else:
			vpc_obj.mark_mac_address_as_allocated(mac)

		status = spec['status']
		if status == ep_status_init:
			# Move the status to allocated an invoke the bouncer
			status = ep_status_allocated

		elif status == ep_status_allocated:
			logger.info("(BUG) No other entity should move the status to allocated except the endpoint operator")
			pass

		elif status == ep_status_ready:
			logger.info("Good to know that status is ready")
			pass

		elif status == ep_status_provisioned:
			logger.info("Good to know that status is provisioned")
			pass

		ep = Endpoint(name, itf, veth, netns, droplet, droplet_obj, vpc, net, vni, status,
			gw, ip, prefix, mac, ep_type, self.obj_api)

		# Update the vpc store and cascade to next processing steps (e.g. bouncers)
		if ep_type == 'simple':
			self.vs.get(vpc).update_simple_endpoint(ep)

		if update_endpoint:
			ep.update_object()

	def on_create(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)

	def on_resume(self, body, spec, **kwargs):
		self.on_update(body, spec, **kwargs)



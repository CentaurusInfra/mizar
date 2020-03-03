import uuid
import logging
from common.rpc import TrnRpc
from common.constants import *
from common.common import *
from obj.bouncer import Bouncer
from common.cidr import Cidr
from kubernetes.client.rest import ApiException

logger = logging.getLogger()

class Net(object):
	def __init__(self, name, obj_api, opr_store, spec=None):
		self.name = name
		self.vpc = OBJ_DEFAULTS.default_ep_vpc
		self.vni = OBJ_DEFAULTS.default_vpc_vni
		self.cidr = Cidr(OBJ_DEFAULTS.default_net_prefix, OBJ_DEFAULTS.default_net_ip)
		self.n_bouncers = OBJ_DEFAULTS.default_n_bouncers
		self.n_allocated_bouncers = 0
		self.bouncers = {}
		self.endpoints = {}
		self.obj_api = obj_api
		self.store = opr_store
		self.gw = self.cidr.gw
		self.status = OBJ_STATUS.net_status_init
		if spec is not None:
			self.set_obj_spec(spec)

	def get_obj_spec(self):
		self.obj = {
			"ip": self.cidr.ip,
			"prefix": self.cidr.prefixlen,
			"vni": self.vni,
			"vpc": self.vpc,
			"bouncers": self.n_bouncers,
			"status": self.status
		}

		return self.obj

	def set_obj_spec(self, spec):
		self.status = get_spec_val('type', spec)
		self.vpc = get_spec_val('vpc', spec)
		self.vni = get_spec_val('vni', spec)
		self.n_bouncers = int(get_spec_val('bouncers', spec, OBJ_DEFAULTS.default_n_bouncers))
		ip = get_spec_val('ip', spec, OBJ_DEFAULTS.default_net_ip)
		prefix = get_spec_val('prefix', spec, OBJ_DEFAULTS.default_net_prefix)
		self.cidr = Cidr(prefix, ip)
		self.gw = self.cidr.gw

	# K8s APIs
	def get_name(self):
		return self.name

	def get_plural(self):
		return "nets"

	def get_kind(self):
		return "Net"

	def store_update_obj(self):
		if self.store is None:
			return
		self.store.update_net(self)

	def store_delete_obj(self):
		if self.store is None:
			return
		self.store.delete_net(self.name)

	def create_obj(self):
		return kube_create_obj(self)

	def update_obj(self):
		return kube_update_obj(self)

	def delete_obj(self):
		return kube_delete_obj(self)

	def watch_obj(self, watch_callback):
		return kube_watch_obj(self, watch_callback)

	def set_vni(self, vni):
		self.vni = vni

	def set_status(self, status):
		self.status = status

	def get_gw_ip(self):
		return str(self.cidr.get_ip(1))

	def get_tunnel_id(self):
		return str(self.vni)

	def get_nip(self):
		return str(self.cidr.ip)

	def get_prefixlen(self):
		return str(self.cidr.prefixlen)

	def get_bouncers_ips(self):
		return [str(b.ip) for b in self.bouncers.values()]

	def create_bouncer(self):
		logger.info("Create bouncer for net {}".format(self.name))
		u = str(uuid.uuid4())
		bouncer_name = self.name +'-b-' + u
		b = Bouncer(bouncer_name, self.obj_api, None)
		b.set_vpc(self.vpc)
		b.set_net(self.name)
		b.create_obj()

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

		logger.info("$$ done update_simple_endpoint {} of net {} bouncers {}".format(ep.name, self.name, self.bouncers.keys()))
		ep.status = ep_status_ready

		ep.droplet_obj.load_transit_agent_xdp(ep)
		ep.droplet_obj.update_agent_metadata(ep, self)
		for b in bouncers:
			ep.droplet_obj.update_agent_substrate_ep(ep, b.droplet_obj)

		#update agent metadata
		ep.update_object()

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
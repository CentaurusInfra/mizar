import logging

logger = logging.getLogger()

class Bouncer(object):
	def __init__(self, name, vpc, net, ip, droplet, droplet_obj):
		self.name = name
		self.droplet = droplet
		self.vpc = vpc
		self.net = net
		self.ip = ip
		self.droplet_obj = droplet_obj

	def update_simple_endpoint(self, ep):
		logger.info("Bouncer {} update_simple_endpoint {} on droplet {}".format(self.name, ep.name, ep.droplet))
		self.droplet_obj.update_ep(ep)
		self.droplet_obj.update_substrate_ep(ep.droplet_obj)




#         self.droplet.update_ep(ep)
#         # Now update the mac address of the endpoint's host
#         if ep.host is not None:
#             self.droplet.update_substrate_ep(ep.host)



#         def update_ep(self, ep, expect_fail=False):
#         if ep.host is not None:
#             log_string = "[DROPLET {}]: update_ep {} hosted at {}".format(
#                 self.id, ep.ip, ep.host.id)
#         else:
#             log_string = "[DROPLET {}]: update_ep for a phantom ep {}".format(
#                 self.id, ep.ip)
#         peer = ""

#         # Only detail veth info if the droplet is also a host
#         if (ep.host and self.ip == ep.host.ip):
#             peer = ep.get_veth_peer()

#         jsonconf = {
#             "tunnel_id": ep.get_tunnel_id(),
#             "ip": ep.get_ip(),
#             "eptype": ep.get_eptype(),
#             "mac": ep.get_mac(),
#             "veth": ep.get_veth_name(),
#             "remote_ips": ep.get_remote_ips(),
#             "hosted_iface": peer
#         }
#         jsonconf = json.dumps(jsonconf)
#         jsonkey = {
#             "tunnel_id": ep.get_tunnel_id(),
#             "ip": ep.get_ip(),
#         }
#         key = ("ep " + self.phy_itf, json.dumps(jsonkey))
#         cmd = f'''{self.trn_cli_update_ep} \'{jsonconf}\''''
#         self.do_update_increment(
#             log_string, cmd, expect_fail, key, self.endpoint_updates)

# def update_substrate_ep(self, droplet, expect_fail=False):
#         log_string = "[DROPLET {}]: update_substrate_ep for droplet {}".format(
#             self.id, droplet.ip)
#         jsonconf = droplet.get_substrate_ep_json()
#         jsonkey = {
#             "tunnel_id": "0",
#             "ip": droplet.ip,
#         }
#         key = ("ep_substrate " + self.phy_itf,
#                json.dumps(jsonkey))
#         cmd = f'''{self.trn_cli_update_ep} \'{jsonconf}\''''
#         self.do_update_increment(
#             log_string, cmd, expect_fail, key, self.substrate_updates)
import logging
import json
from common.common import run_cmd

logger = logging.getLogger()


class Droplet(object):

	def __init__(self, name, ip, mac):
		self.name = name
		self.ip = ip
		self.mac = mac
		self.phy_itf = 'eth0'

		# transitd cli commands
		self.trn_cli = f'''/trn_bin/transit -s {self.ip} '''
		self.trn_cli_load_transit_xdp = f'''{self.trn_cli} load-transit-xdp -i {self.phy_itf} -j'''
		self.trn_cli_unload_transit_xdp = f'''{self.trn_cli} unload-transit-xdp -i {self.phy_itf} -j'''
		self.trn_cli_update_vpc = f'''{self.trn_cli} update-vpc -i {self.phy_itf} -j'''
		self.trn_cli_get_vpc = f'''{self.trn_cli} get-vpc -i {self.phy_itf} -j'''
		self.trn_cli_delete_vpc = f'''{self.trn_cli} delete-vpc -i {self.phy_itf} -j'''
		self.trn_cli_update_net = f'''{self.trn_cli} update-net -i {self.phy_itf} -j'''
		self.trn_cli_get_net = f'''{self.trn_cli} get-net -i {self.phy_itf} -j'''
		self.trn_cli_delete_net = f'''{self.trn_cli} delete-net -i {self.phy_itf} -j'''
		self.trn_cli_update_ep = f'''{self.trn_cli} update-ep -i {self.phy_itf} -j'''
		self.trn_cli_get_ep = f'''{self.trn_cli} get-ep -i {self.phy_itf} -j'''
		self.trn_cli_delete_ep = f'''{self.trn_cli} delete-ep -i {self.phy_itf} -j'''
		self.trn_cli_load_pipeline_stage = f'''{self.trn_cli} load-pipeline-stage -i {self.phy_itf} -j'''

		self.trn_cli_load_transit_agent_xdp = f'''{self.trn_cli} load-agent-xdp'''
		self.trn_cli_unload_transit_agent_xdp = f'''{self.trn_cli} unload-agent-xdp'''
		self.trn_cli_update_agent_metadata = f'''{self.trn_cli} update-agent-metadata'''
		self.trn_cli_get_agent_metadata = f'''{self.trn_cli} get-agent-metadata'''
		self.trn_cli_delete_agent_metadata = f'''{self.trn_cli} delete-agent-metadata'''
		self.trn_cli_update_agent_ep = f'''{self.trn_cli} update-agent-ep'''
		self.trn_cli_get_agent_ep = f'''{self.trn_cli} get-agent-ep'''
		self.trn_cli_delete_agent_ep = f'''{self.trn_cli} delete-agent-ep'''

	def get_substrate_ep_json(self):
		jsonconf = {
			"tunnel_id": "0",
			"ip": self.ip,
			"eptype": "0",
			"mac": self.mac,
			"veth": "",
			"remote_ips": [""],
			"hosted_iface": ""
		}
		jsonconf = json.dumps(jsonconf)
		return jsonconf

	def update_substrate_ep(self, droplet):
		jsonconf = droplet.get_substrate_ep_json()
		cmd = f'''{self.trn_cli_update_ep} \'{jsonconf}\''''
		logger.info("update_substrate_ep: {}".format(cmd))
		returncode, text = run_cmd(cmd)
		logger.info("returns {} {}".format(returncode, text))

	def update_ep(self, ep, expect_fail=False):
		peer = ""

		# Only detail veth info if the droplet is also a host
		if (ep.droplet_obj and self.ip == ep.droplet_obj.ip):
			peer = ep.get_veth_peer()

		jsonconf = {
			"tunnel_id": ep.get_tunnel_id(),
			"ip": ep.get_ip(),
			"eptype": ep.get_eptype(),
			"mac": ep.get_mac(),
			"veth": ep.get_veth_name(),
			"remote_ips": ep.get_remote_ips(),
			"hosted_iface": peer
		}

		jsonconf = json.dumps(jsonconf)
		jsonkey = {
			"tunnel_id": ep.get_tunnel_id(),
			"ip": ep.get_ip(),
		}
		key = ("ep " + self.phy_itf, json.dumps(jsonkey))
		cmd = f'''{self.trn_cli_update_ep} \'{jsonconf}\''''
		logger.info("update_ep: {}".format(cmd))
		returncode, text = run_cmd(cmd)
		logger.info("returns {} {}".format(returncode, text))
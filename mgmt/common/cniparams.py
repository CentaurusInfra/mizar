import os
import json
import subprocess
import logging

logger = logging.getLogger()

class CniParams:
	def __init__(self, stdin):
		#logging.info(stdin)
		self.command = os.environ.get("CNI_COMMAND") # ADD | DEL | VERSION
		self.container_id = os.environ.get("CNI_CONTAINERID")
		self.netns = os.environ.get("CNI_NETNS")
		self.container_pid = None
		if (self.netns != ""):
			self.container_pid =  self.netns.split("/")[2]
		self.interface = os.environ.get("CNI_IFNAME")
		self.cni_path = os.environ.get("CNI_PATH")
		self.cni_args = os.environ.get("CNI_ARGS")
		self.cni_args_dict = {}

		argarray = [i.split('=') for i in self.cni_args.split(';')]
		for a in argarray:
			self.cni_args_dict[a[0]] = a[1]

		# Load network configuration parameters
		config_json = json.loads(stdin)

		# expected parameters in the CNI specification:
		self.cni_version = config_json["cniVersion"]
		self.network_name = config_json["name"]
		self.plugin = config_json["type"]
		self.default_vpc = config_json["default_vpc"]
		self.default_net = config_json["default_net"]
		if "args" in config_json:
			self.args = config_json["args"]
		if "ipMasq" in config_json:
			self.ip_masq = config_json["ipMasq"]
			self.ipam = config_json["ipam"]
		if "dns" in config_json:
			self.dns = config_json["dns"]

		self.k8sconfig = config_json["k8sconfig"]

		logger.info("read params")
		cmd = 'hostname'
		r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		self.droplet = r.stdout.read().decode().strip()
		logger.info("done reading params {}".format(self.droplet))
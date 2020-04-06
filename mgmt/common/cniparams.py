# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
		self.default_vni = config_json["default_vni"]
		if "args" in config_json:
			self.args = config_json["args"]
		if "ipMasq" in config_json:
			self.ip_masq = config_json["ipMasq"]
			self.ipam = config_json["ipam"]
		if "dns" in config_json:
			self.dns = config_json["dns"]

		self.k8sconfig = config_json["k8sconfig"]

		logger.info("read params")
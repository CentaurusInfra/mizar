#!/usr/bin/python3
import os
import sys
import json
import logging
import uuid
import pprint
import subprocess
from kubernetes import client, config, watch

logging.basicConfig(level=logging.INFO, filename='/tmp/cni.log')

sys.stderr = open('/tmp/cni.stderr', 'w')

# apiVersion: apiextensions.k8s.io/v1beta1
# kind: CustomResourceDefinition
# metadata:
#   name: endpoints.mizar.com
# spec:
#   scope: Namespaced
#   group: mizar.com
#   versions:
#     - name: v1
#       served: true
#       storage: true
#   names:
#     kind: Endpoint
#     plural: endpoints
#     singular: endpoint
#     shortNames:
#       - ep
#       - eps
#   additionalPrinterColumns:
#     - name: Type
#       type: string
#       priority: 0
#       JSONPath: .spec.type
#       description: The type of the endpoint

class k8sParams:
	def __init__(self, stdin):
		#logging.info(stdin)
		self.command = os.environ.get("CNI_COMMAND") # ADD | DEL | VERSION
		self.container_id = os.environ.get("CNI_CONTAINERID")
		self.netns = os.environ.get("CNI_NETNS")
		self.container_pid = None
		if (self.netns != ""):
			self.container_pid =  os.environ.get("CNI_NETNS").split("/")[2]
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

		logging.info("read params")
		cmd = 'hostname'
		r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
		self.droplet = r.stdout.read().decode().strip()
		logging.info("done reading params {}".format(self.droplet))

class endpoint:
	def __init__(self, droplet, vpc, net, interface, netns, args, core_api, obj_api):
		self.core_api = core_api
		self.obj_api = obj_api
		self.interface = interface
		self.vpc = vpc
		self.net = net
		self.mac = ""
		self.netns = netns
		self.ip = ""
		self.prefix = ""
		self.gw = ""
		self.interface_index = "0"
		self.status = "init"
		self.name = ""
		if 'K8S_POD_NAME' in args:
			self.name = args['K8S_POD_NAME']
		self.name = 'simple-ep-' + self.name
		self.droplet = droplet

		self.obj = {
			"apiVersion": "mizar.com/v1",
			"kind": "Endpoint",
			"metadata": {
				"name": self.name
			},
			"spec": {
				"type": "simple",
				"status": self.status,
				"vpc": self.vpc,
				"net": self.net,
				"droplet": self.droplet
			}
		}

	def create_endpoint_obj(self):
		# create the resource
		self.obj_api.create_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural="endpoints",
			body=self.obj,
		)
		logging.info("test_ep Resource created {}".format(self.name))


	def watch_endpoint_obj(self):
		watcher = watch.Watch()
		stream = watcher.stream(self.obj_api.list_namespaced_custom_object,
					group="mizar.com",
					version="v1",
					namespace="default",
					plural="endpoints",
					field_selector = "metadata.name={}".format(self.name),
					watch = True
				)

		for event in stream:
			name = event['object']['metadata']['name']
			status = event['object']['spec']['status']
			logging.info("!!Recieved name: {}, status: {}".format(name, status))
			if name != self.name:
				continue
			if status != "ready":
				continue
			logging.info("!!Filtered name: {}, status: {}".format(name, status))
			watcher.stop()
			return True

	def is_endpoint_ready(self):
		return True

	def create_endpoint(self):
		#create veth pair
		pass

class cni:
	def __init__(self, params):
		self.params = params
		self.core_api=client.CoreV1Api()
		self.obj_api = client.CustomObjectsApi()

	def exec_add(self):
		#logging.info("add")
		#logging.info(self.params.cni_args_dict)
		ep = endpoint(self.params.droplet, self.params.default_vpc, self.params.default_net, self.params.interface, self.params.netns, self.params.cni_args_dict, self.core_api, self.obj_api)
		ep.create_endpoint_obj()
		if ep.watch_endpoint_obj():
			logging.info("!!READY")
		#logging.info("Done watching ,,,...!!!")

		result = {
			"cniVersion": self.params.cni_version,
			"interfaces": [
				{
					"name": ep.interface,
					"mac": ep.mac,
					"sandbox": ep.netns
				}
			],
			"ips":[
				{
					"version": "4",
					"address": "{}/{}".format(ep.ip,ep.prefix),
					"gateway": ep.gw,
					"interface": ep.interface_index
				}
			]
		}

		return json.dumps(result)

	def exec_delete(self):
		logging.info("delete")

	def exec_version(self):
		logging.info("version")

	def exec(self):
		switcher = {
			'ADD': self.exec_add,
			'DEL': self.exec_delete,
			'VERSION': self.exec_version
		}

		func = switcher.get(self.params.command, lambda: "Unsuported cni command")
		return func()


def main():

	params = k8sParams(''.join(sys.stdin.readlines()))
	config.load_kube_config(config_file=params.k8sconfig)
	c = cni(params)
	print(c.exec(), file=sys.stdout)

	# # it's my custom resource defined as Dict
	# test_ep = {
	# 	"apiVersion": "mizar.com/v1",
	# 	"kind": "Endpoint",
	# 	"metadata": {"name": "mizartest2-ep"},
	# 	"spec": {
	# 		"type": "simple"
	# 	}
	# }

	# # create the resource
	# obj_api.create_namespaced_custom_object(
	# 	group="mizar.com",
	# 	version="v1",
	# 	namespace="default",
	# 	plural="endpoints",
	# 	body=test_ep,
	# )
	# logging.info("test_ep Resource created")


main()
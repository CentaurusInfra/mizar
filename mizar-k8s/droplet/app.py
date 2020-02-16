#!/usr/bin/python3
import logging
import subprocess
from kubernetes import client, config, watch

logging.basicConfig(level=logging.INFO)

cmd = 'nsenter -t 1 -m -u -n -i ip addr show eth0 | grep "inet\\b" | awk \'{print $2}\' | cut -d/ -f1'
r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
ip = r.stdout.read().decode().strip()

cmd = 'nsenter -t 1 -m -u -n -i ip addr show eth0 | grep "link/ether\\b" | awk \'{print $2}\' | cut -d/ -f1'
r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
mac = r.stdout.read().decode().strip()

cmd = 'nsenter -t 1 -m -u -n -i hostname'
r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
name = r.stdout.read().decode().strip()

config.load_incluster_config()
obj_api = client.CustomObjectsApi()

obj = {
	"apiVersion": "mizar.com/v1",
	"kind": "Droplet",
	"metadata": {
		"name": name
	},
	"spec": {
		"mac": ip,
		"ip": mac
	}
}

try:
	obj_api.create_namespaced_custom_object(
		group="mizar.com",
		version="v1",
		namespace="default",
		plural="droplets",
		body=obj,
	)
	logging.info("droplet Resource created")
except:
	logging.info("droplet Resource exists")

while 1:
	pass
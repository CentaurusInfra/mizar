#!/usr/bin/python3
import logging
import subprocess
import rpyc
import inspect
from kubernetes import client, config, watch
from rpyc.utils.server import ThreadedServer
from daemon.cni_service import CniService

logging.basicConfig(level=logging.INFO)

# Setup the droplet's host
script = (f''' bash -c '\
nsenter -t 1 -m -u -n -i rm /etc/cni/net.d/10-kindnet.conflist &&\
nsenter -t 1 -m -u -n -i /etc/init.d/rpcbind restart && \
nsenter -t 1 -m -u -n -i /etc/init.d/rsyslog restart && \
nsenter -t 1 -m -u -n -i ip link set dev eth0 up mtu 9000' ''')

r = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE)
output = r.stdout.read().decode().strip()
logging.info("Setup done")

### Get the droplet IP/MAC
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
		"mac": mac,
		"ip": ip
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


cmd = "nsenter -t 1 -m -u -n -i ip link set dev eth0 xdpgeneric off"

r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
output = r.stdout.read().decode().strip()
logging.info("Removed existing XDP program: {}".format(output))

cmd = "nsenter -t 1 -m -u -n -i /trn_bin/transitd &"
r = subprocess.Popen(cmd, shell=True)
logging.info("Running transitd")

config = '{"xdp_path": "/trn_xdp/trn_transit_xdp_ebpf_debug.o", "pcapfile": "/bpffs/transit_xdp.pcap"}'
# Load the xdp program on to eth0 of the host machine
cmd = (f''' nsenter -t 1 -m -u -n -i \
/trn_bin/transit -s {ip} \
load-transit-xdp -i eth0 -j \
'{config}' ''')

r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
output = r.stdout.read().decode().strip()
logging.info("Running load-transit-xdp: {}".format(output))

logging.info("Droplet {} is ready".format(name))

choice = 'ThreadedServer'  # Debugging
svc_server = None
server_class = {}
# Populate for 'ForkingServer', 'GeventServer', 'OneShotServer', 'ThreadPoolServer', and 'ThreadedServer'
for name, value in inspect.getmembers(rpyc.utils.server, inspect.isclass):
	if rpyc.utils.server.Server in getattr(value, '__mro__', []):
		server_class[name] = value
print(server_class.keys())
svc_server = server_class[choice]
svc = svc_server(service=CniService, hostname='localhost', port=18861, protocol_config={'allow_all_attrs': True})
svc.start()
logging.info("Server ####!!!")


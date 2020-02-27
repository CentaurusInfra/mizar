#!/usr/bin/python3
import logging
import subprocess
import rpyc
import inspect
from common.common import host_nsenter
from kubernetes import client, config
from kubernetes.client import Configuration
from rpyc.utils.server import ThreadedServer
from daemon.cni_service import CniService

logging.basicConfig(level=logging.DEBUG)

# Setup the droplet's host
script = (f''' bash -c '\
nsenter -t 1 -m -u -n -i rm /etc/cni/net.d/10-kindnet.conflist &&\
nsenter -t 1 -m -u -n -i /etc/init.d/rpcbind restart && \
nsenter -t 1 -m -u -n -i /etc/init.d/rsyslog restart && \
nsenter -t 1 -m -u -n -i ip link set dev eth0 up mtu 9000' ''')

r = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE)
output = r.stdout.read().decode().strip()
logging.info("Setup done")

c = config.load_incluster_config()
CniService.config = Configuration._default
cert_file = Configuration._default.ssl_ca_cert
obj_api = client.CustomObjectsApi()
CniService.configure_droplet(obj_api)

with open(cert_file) as f:
	CniService.cert = f.read()

host_nsenter(1)

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


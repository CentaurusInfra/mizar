#!/usr/bin/python3
import logging
import subprocess
from kubernetes import client, config, watch

logging.basicConfig(level=logging.INFO)

# Setup the droplet's host
script = (f''' bash -c '\
mkdir -p /mizar/mizar && \
cp -r /var/mizar/* /mizar/mizar/ &&\
nsenter -t 1 -m -u -n -i apt-get update -y && nsenter -t 1 -m -u -n -i apt-get install -y \
    sudo \
    rpcbind \
    rsyslog \
    libelf-dev \
    iproute2  \
    net-tools \
    iputils-ping \
    ethtool \
    curl \
    python3 \
    python3-pip \
  	&& \
nsenter -t 1 -m -u -n -i /etc/init.d/rpcbind restart && \
nsenter -t 1 -m -u -n -i /etc/init.d/rsyslog restart && \
nsenter -t 1 -m -u -n -i ip link set dev eth0 up mtu 9000 && \
nsenter -t 1 -m -u -n -i ln -snf /sys/fs/bpf /bpffs && \
nsenter -t 1 -m -u -n -i ln -snf /home/mizar/droplet/build/bin /trn_bin && \
nsenter -t 1 -m -u -n -i ln -snf /home/mizar/droplet/build/xdp /trn_xdp ' ''')

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

while 1:
	pass
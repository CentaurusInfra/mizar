
import grpc
import time
import subprocess
import json
from google.protobuf import empty_pb2
from concurrent import futures
from mizar.daemon.interface_service import InterfaceServer
from mizar.daemon.droplet_service import DropletServer
from mizar.common.constants import CONSTANTS
from mizar.common.common import *
import mizar.proto.interface_pb2_grpc as interface_pb2_grpc
import mizar.proto.interface_pb2 as interface_pb2
import mizar.proto.droplet_pb2_grpc as droplet_pb2_grpc
import mizar.proto.droplet_pb2 as droplet_pb2
import os
import logging
import sys


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

POOL_WORKERS = 10


def init(benchmark=True):
    # Setup the droplet's host
    default_itf = get_itf()
    script = (f''' bash -c '\
    nsenter -t 1 -m -u -n -i ls -1 /etc/cni/net.d/*conf* | grep -v '10-mizarcni.conf$' | xargs rm -rf && \
    nsenter -t 1 -m -u -n -i /etc/init.d/rpcbind restart && \
    nsenter -t 1 -m -u -n -i /etc/init.d/rsyslog restart && \
    nsenter -t 1 -m -u -n -i sysctl -w net.ipv4.tcp_mtu_probing=2 && \
    nsenter -t 1 -m -u -n -i ip link set dev eth0 up mtu 9000 && \
    nsenter -t 1 -m -u -n -i mkdir -p /var/run/netns' ''')

    r = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE)
    output = r.stdout.read().decode().strip()
    logging.info("Setup done")

    cmd = 'nsenter -t 1 -m -u -n -i ip addr show ' + f'''{default_itf}''' + ' | grep "inet\\b" | awk \'{print $2}\''
    r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    nodeipmask = r.stdout.read().decode().strip()
    nodeip = nodeipmask.split("/")[0]

    cmd = "nsenter -t 1 -m -u -n -i ip link set dev " + f'''{default_itf}''' + " xdpgeneric off"

    r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = r.stdout.read().decode().strip()
    logging.info("Removed existing XDP program: {}".format(output))

    cmd = "nsenter -t 1 -m -u -n -i /trn_bin/transitd &"
    r = subprocess.Popen(cmd, shell=True)
    logging.info("Running transitd")
    time.sleep(1)

    if benchmark:
        transit_xdp_path = "/trn_xdp/trn_transit_xdp_ebpf.o"
        tc_edt_ebpf_path = "/trn_xdp/trn_edt_tc_ebpf.o"
    else:
        transit_xdp_path = "/trn_xdp/trn_transit_xdp_ebpf_debug.o"
        tc_edt_ebpf_path = "/trn_xdp/trn_edt_tc_ebpf_debug.o"

    config = {
        "xdp_path": transit_xdp_path,
        "pcapfile": "/bpffs/transit_xdp.pcap",
        "xdp_flag": CONSTANTS.XDP_GENERIC
    }
    config = json.dumps(config)
    cmd = (
        f'''nsenter -t 1 -m -u -n -i /trn_bin/transit -s {nodeip} load-transit-xdp -i {default_itf} -j '{config}' ''')

    r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = r.stdout.read().decode().strip()
    logging.info("Running load-transit-xdp: {}".format(output))

    if os.getenv('FEATUREGATE_BWQOS', 'false').lower() in ('false', '0'):
        logging.info("Bandwidth QoS feature is disabled.")
        return

    # Setup mizar bridge, update routes, and load EDT TC eBPF program
    logging.info("Node IP: {}".format(nodeipmask))

    brcmd = f'''nsenter -t 1 -m -u -n -i sysctl -w net.bridge.bridge-nf-call-iptables=0 && \
        nsenter -t 1 -m -u -n -i ip link add {CONSTANTS.MIZAR_BRIDGE} type bridge && \
        nsenter -t 1 -m -u -n -i ip link set dev {CONSTANTS.MIZAR_BRIDGE} up && \
        nsenter -t 1 -m -u -n -i ip link set eth0 master {CONSTANTS.MIZAR_BRIDGE} && \
        nsenter -t 1 -m -u -n -i ip addr add {nodeip} dev {CONSTANTS.MIZAR_BRIDGE} && \
        nsenter -t 1 -m -u -n -i brctl show'''

    dev_default_itf = f'''dev {default_itf}'''
    rtlistcmd = 'nsenter -t 1 -m -u -n -i ip route list | grep "' + f'''{dev_default_itf}''' +'"'

    r = subprocess.Popen(rtlistcmd, shell=True, stdout=subprocess.PIPE)
    rtchanges = []
    while True:
        line = r.stdout.readline()
        if not line:
            break
        rt = line.decode().strip()
        rtkey = rt.partition(dev_default_itf)[0]
        rtdesc = rt.partition(dev_default_itf)[2]
        rnew = 'nsenter -t 1 -m -u -n -i ip route change ' + rtkey + f'''dev {CONSTANTS.MIZAR_BRIDGE}''' + rtdesc
        if 'default' in rt:
            rtchanges.append(rnew)
        else:
            rtchanges.insert(0, rnew)

    rtchangecmd = ""
    if len(rtchanges) > 0:
        for rtc in rtchanges:
            if not rtchangecmd:
                rtchangecmd =  rtc
            else:
                rtchangecmd = rtchangecmd + " && " + rtc
            rtchangecmd = rtchangecmd + " || true"
        rtchangecmd = rtchangecmd + " && "
    rtchangecmd = rtchangecmd + f'''nsenter -t 1 -m -u -n -i ip route list'''

    brscript = (f''' bash -c '{brcmd} && {rtchangecmd}' ''')
    logging.info("Mizar bridge setup script:\n{}\n".format(brscript))
    r = subprocess.Popen(brscript, shell=True, stdout=subprocess.PIPE)
    output = r.stdout.read().decode().strip()
    #TODO: Restore original network config upon error / cleanup
    logging.info("Mizar bridge setup complete.\n{}\n".format(output))

    tcscript = (f''' bash -c '\
    nsenter -t 1 -m -u -n -i tc qdisc add dev {default_itf} clsact && \
    nsenter -t 1 -m -u -n -i tc filter del dev {default_itf} egress && \
    nsenter -t 1 -m -u -n -i tc filter add dev {default_itf} egress bpf da obj {tc_edt_ebpf_path} sec edt && \
    nsenter -t 1 -m -u -n -i tc filter show dev {default_itf} egress' ''')
    r = subprocess.Popen(tcscript, shell=True, stdout=subprocess.PIPE)
    output = r.stdout.read().decode().strip()
    logging.info("Load EDT eBPF program done.\n{}\n".format(output))

    #Setup multi-level QoS for Best-effort and Expedited class traffic
    linkspeed="10gbit"
    burstsize="2k"
    tcscript = (f''' bash -c '\
    nsenter -t 1 -m -u -n -i tc qdisc del dev {CONSTANTS.MIZAR_BRIDGE} root 2> /dev/null || true && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} root handle 1: prio bands 6 priomap 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 1:1 handle 11: pfifo && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 1:2 handle 12: htb r2q 6 && \
    nsenter -t 1 -m -u -n -i tc class add dev {CONSTANTS.MIZAR_BRIDGE} parent 12: classid 12:1 htb rate {linkspeed} burst {burstsize} && \
    nsenter -t 1 -m -u -n -i tc class add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:1 classid 12:11 htb rate {linkspeed} ceil {linkspeed} burst {linkspeed} prio 1 && \
    nsenter -t 1 -m -u -n -i tc class add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:1 classid 12:12 htb rate {linkspeed} ceil {linkspeed} burst {linkspeed} prio 2 && \
    nsenter -t 1 -m -u -n -i tc class add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:1 classid 12:13 htb rate {linkspeed} ceil {linkspeed} burst {linkspeed} prio 3 && \
    nsenter -t 1 -m -u -n -i tc class add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:1 classid 12:14 htb rate {linkspeed} ceil {linkspeed} burst {linkspeed} prio 4 && \
    nsenter -t 1 -m -u -n -i tc class add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:1 classid 12:15 htb rate {linkspeed} ceil {linkspeed} burst {linkspeed} prio 5 && \
    nsenter -t 1 -m -u -n -i tc class add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:1 classid 12:16 htb rate {linkspeed} ceil {linkspeed} burst {linkspeed} prio 6 && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:11 handle 1211: sfq perturb 10 && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:12 handle 1212: sfq perturb 10 && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:13 handle 1213: sfq perturb 10 && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:14 handle 1214: sfq perturb 10 && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:15 handle 1215: sfq perturb 10 && \
    nsenter -t 1 -m -u -n -i tc qdisc add dev {CONSTANTS.MIZAR_BRIDGE} parent 12:16 handle 1216: sfq perturb 10 && \
    nsenter -t 1 -m -u -n -i tc filter add dev {CONSTANTS.MIZAR_BRIDGE} parent 1: prio 1 protocol ip u32 match ip tos 0xB8 0xff flowid 1:1 && \
    nsenter -t 1 -m -u -n -i tc filter add dev {CONSTANTS.MIZAR_BRIDGE} parent 1: prio 2 protocol ip u32 match ip tos 0x80 0xff flowid 1:2 && \
    nsenter -t 1 -m -u -n -i tc filter add dev {CONSTANTS.MIZAR_BRIDGE} parent 1: prio 3 protocol ip u32 match ip tos 0x60 0xff flowid 1:3 && \
    nsenter -t 1 -m -u -n -i tc filter add dev {CONSTANTS.MIZAR_BRIDGE} parent 1: prio 4 protocol ip u32 match ip tos 0x40 0xff flowid 1:4 && \
    nsenter -t 1 -m -u -n -i tc filter add dev {CONSTANTS.MIZAR_BRIDGE} parent 1: prio 5 protocol ip u32 match ip tos 0x00 0xff flowid 1:5 && \
    nsenter -t 1 -m -u -n -i tc filter add dev {CONSTANTS.MIZAR_BRIDGE} parent 1: prio 6 protocol ip u32 match ip tos 0x20 0xff flowid 1:6 && \
    nsenter -t 1 -m -u -n -i tc -s qdisc ls dev {CONSTANTS.MIZAR_BRIDGE} && \
    nsenter -t 1 -m -u -n -i tc -s class ls dev {CONSTANTS.MIZAR_BRIDGE}' ''')
    r = subprocess.Popen(tcscript, shell=True, stdout=subprocess.PIPE)
    output = r.stdout.read().decode().strip()
    logging.info("Multi-level QoS setup done.\n{}\n".format(output))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=POOL_WORKERS))

    droplet_pb2_grpc.add_DropletServiceServicer_to_server(
        DropletServer(), server
    )

    interface_pb2_grpc.add_InterfaceServiceServicer_to_server(
        InterfaceServer(), server
    )

    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Transit daemon is ready")
    try:
        while True:
            time.sleep(100000)
    except KeyboardInterrupt:
        server.stop(0)


init()
serve()

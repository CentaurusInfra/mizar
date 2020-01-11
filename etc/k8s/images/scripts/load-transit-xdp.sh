#!/bin/bash

# Wait for transitd to run before loading xdp
nsenter -t 1 -m -u -n -i ps -aux | pgrep transitd > /dev/null 2>&1
running=$?
while [[ $running  -eq 1 ]]; do
    sleep 10
    nsenter -t 1 -m -u -n -i ps -aux | pgrep transitd > /dev/null 2>&1
    running=$?
done
# Load the xdp program on to eth0 of the host machine
nsenter -t 1 -m -u -n -i /trn_bin/transit -s \
$(nsenter -t 1 -m -u -n -i ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1) \
load-transit-xdp -i eth0 -j \
'{"xdp_path": "/trn_xdp/trn_transit_xdp_ebpf_debug.o", "pcapfile": "/bpffs/transit_xdp.pcap"}' \
&& echo "mizar-complete" && sleep infinity

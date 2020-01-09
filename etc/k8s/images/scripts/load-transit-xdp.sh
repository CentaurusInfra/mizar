#!/bin/bash

(sleep 5 && nsenter -t 1 -m -u -n -i /trn_bin/transit -s $(nsenter -t 1 -m -u -n -i ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1) load-transit-xdp -i eth0 -j '{"xdp_path": "/trn_xdp/trn_transit_xdp_ebpf_debug.o", "pcapfile": "/bpffs/transit_xdp.pcap"}' && echo "mizar-complete" && sleep infinity)

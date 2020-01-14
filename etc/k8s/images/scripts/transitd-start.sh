#!/bin/bash

nsenter -t 1 -m -u -n -i ip link set dev eth0 xdpgeneric off # unload any existing xdp program
nsenter -t 1 -m -u -n -i /trn_bin/transitd

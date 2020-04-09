#!/bin/bash
nc -l -p 9001 > /tmp/nc_tcp.recv &
nc -u -l -p 5001 > /tmp/nc_udp.recv &
python3 -m http.server > /tmp/httpd.log 2>&1 &
while true; do echo "test"; sleep 2; done

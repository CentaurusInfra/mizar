#!/bin/bash

/etc/init.d/rpcbind restart
/etc/init.d/rsyslog restart
/etc/init.d/openvswitch-switch restart
ip link set dev eth0 up mtu 9000

nohup /home/ubuntu/mizar/build/bin/transitd &

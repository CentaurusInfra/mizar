#!/bin/bash
#Int_face="lshw -class network | grep -A 1 'bus info' | grep name | awk -F': ' '{print $2}'"
/etc/init.d/rpcbind restart
/etc/init.d/rsyslog restart
/etc/init.d/openvswitch-switch restart
ip link set dev lshw -class network | grep -A 1 'bus info' | grep name | awk -F': ' '{print $2}' up mtu 9000

cp /home/ubuntu/mizar/etc/transit.service /etc/systemd/system/

sudo systemctl daemon-reload
systemctl start transit
systemctl enable transit

#!/bin/bash

sudo apt-get update
sudo apt-get install -y \
    build-essential clang-7 llvm-7 \
    rpcbind \
    rsyslog \
    libelf-dev \
    python3 \
    python3-pip \
    libcmocka-dev \
    lcov \
    docker.io \
    openvswitch-switch
sudo pip3 install --upgrade pip

sudo pip3 install netaddr docker


rm -f /bpffs
rm -f /trn_xdp
rm -f /usr/bin/transit
rm -f /usr/bin/transitd
rm -rf /home/ubuntu/mizar

systemctl stop transit
systemctl disable transit
rm -f /etc/systemd/system/transit.service

systemctl unmask docker.service
systemctl unmask docker.socket
systemctl start docker
systemctl enable docker

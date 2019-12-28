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
    lcov

sudo apt install docker.io
sudo pip3 install netaddr docker
sudo systemctl unmask docker.service
sudo systemctl unmask docker.socket
sudo systemctl start docker
sudo systemctl enable docker

sudo pkill -9 transitd
rm -rf /home/ubuntu/mizar

git clone --recurse-submodules -j8 https://github.com/futurewei-cloud/mizar.git /home/ubuntu/mizar

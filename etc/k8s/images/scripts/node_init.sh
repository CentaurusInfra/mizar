#!/bin/bash
nsenter -t 1 -m -u -n -i rm -rf ~/mizar
nsenter -t 1 -m -u -n -i apt-get update -y && nsenter -t 1 -m -u -n -i apt-get install -y \
    sudo \
    rpcbind \
    rsyslog \
    build-essential \
    clang-7 \
    llvm-7 \
    libelf-dev \
    openvswitch-switch \
    iproute2  \
    net-tools \
    iputils-ping \
    ethtool \
    curl \
    python3 \
    python3-pip \
    netcat \
    libcmocka-dev \
    lcov \
    git && \
nsenter -t 1 -m -u -n -i pip3 install httpserver netaddr && \
nsenter -t 1 -m -u -n -i /etc/init.d/rpcbind restart && \
nsenter -t 1 -m -u -n -i /etc/init.d/rsyslog restart && \
nsenter -t 1 -m -u -n -i ip link set dev eth0 up mtu 9000 && \
nsenter -t 1 -m -u -n -i /etc/init.d/openvswitch-switch restart && \
nsenter -t 1 -m -u -n -i git clone --recurse-submodules -j8 https://github.com/futurewei-cloud/mizar.git ~/mizar && \
nsenter -t 1 -m -u -n -i make -C /root/mizar && \
nsenter -t 1 -m -u -n -i ln -snf /sys/fs/bpf /bpffs && \
nsenter -t 1 -m -u -n -i ln -snf ~/mizar/build/bin /trn_bin && \
nsenter -t 1 -m -u -n -i ln -snf ~/mizar/build/xdp /trn_xdp && \
echo "done" && sleep infinity
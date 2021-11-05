FROM ubuntu:latest
RUN apt-get update -y && apt-get install -y \
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
        lcov
RUN pip3 install --upgrade pip
RUN pip3 install httpserver netaddr

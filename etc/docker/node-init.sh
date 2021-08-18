#!/bin/bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Catherine Lu      <@clu2xlu>
#          Hong Chang        <@Hong-Chang>
#          Sherif Abdelwahab <@zasherif>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

cp -rf /var/mizar /home/
mkdir -p /etc/cni/net.d
# check if python is installed ,if yes and check version and install dev pkgs accordingly
pyversion="3.7"
version=$(nsenter -t 1 -m -u -n -i python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
parsedVersion=$(echo "${version//./}")
if [[ -z "$version" ]] ; then
  echo "No Python!"
  # continue with 3.7
elif [[ "$parsedVersion" -gt "37" ]] ; then
  echo "Valid version $version"
  pyversion=$version
fi
echo "python "$pyversion

nsenter -t 1 -m -u -n -i apt-get update -y && nsenter -t 1 -m -u -n -i apt-get install -y \
    sudo \
    rpcbind \
    rsyslog \
    libelf-dev \
    iproute2  \
    net-tools \
    iputils-ping \
    bridge-utils \
    ethtool \
    curl \
    python$pyversion \
    lcov \
    python$pyversion-dev \
    python3-apt \
    python3-testresources \
    libcmocka-dev \
    python3-pip && \
if [[ "$parsedVersion" -lt "37" ]] ; then
  nsenter -t 1 -m -u -n -i update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1 &&
  nsenter -t 1 -m -u -n -i update-alternatives --install /usr/bin/python3 python3 /usr/bin/python$pyversion 2 &&
  nsenter -t 1 -m -u -n -i update-alternatives --set python3 /usr/bin/python$pyversion &&
  nsenter -t 1 -m -u -n -i ln -snf /usr/lib/python3/dist-packages/apt_pkg.cpython-36m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/apt_pkg.so
fi
nsenter -t 1 -m -u -n -i mkdir -p /opt/cni/bin && \
nsenter -t 1 -m -u -n -i mkdir -p /etc/cni/net.d && \
nsenter -t 1 -m -u -n -i ln -snf /var/mizar/mizar/cni.py /opt/cni/bin/mizarcni && \
nsenter -t 1 -m -u -n -i pip3 install --upgrade protobuf && \
nsenter -t 1 -m -u -n -i pip3 install --ignore-installed /var/mizar/ && \
nsenter -t 1 -m -u -n -i ln -snf /sys/fs/bpf /bpffs && \
nsenter -t 1 -m -u -n -i ln -snf /var/mizar/build/bin /trn_bin && \
nsenter -t 1 -m -u -n -i ln -snf /var/mizar/build/xdp /trn_xdp && \
nsenter -t 1 -m -u -n -i cp -f /var/mizar/etc/cni/10-mizarcni.conf /etc/cni/net.d/10-mizarcni.conf && \
nsenter -t 1 -m -u -n -i ln -snf /var/mizar/build/tests/mizarcni.config /etc/mizarcni.config && \
echo "mizar-complete"

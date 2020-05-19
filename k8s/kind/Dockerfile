# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>

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

FROM kindest/node:v1.18.2
RUN apt-get update -y
RUN apt-get install -y apt-utils
RUN apt-get install -y sudo
RUN apt-get install -y vim
RUN apt-get install -y rpcbind
RUN apt-get install -y rsyslog
RUN apt-get install -y libelf-dev
RUN apt-get install -y iproute2
RUN apt-get install -y net-tools
RUN apt-get install -y iputils-ping
RUN apt-get install -y ethtool
RUN apt-get install -y curl
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN mkdir -p /var/mizar/
RUN mkdir -p /opt/cni/bin
RUN mkdir -p /etc/cni/net.d
COPY . /var/mizar/
RUN pip3 install /var/mizar/
RUN ln -snf /sys/fs/bpf /bpffs
RUN ln -snf /var/mizar/build/bin /trn_bin
RUN ln -snf /var/mizar/build/xdp /trn_xdp
RUN ln -snf /var/mizar/etc/cni/10-mizarcni.conf /etc/cni/net.d/10-mizarcni.conf
RUN ln -snf /var/mizar/mizar/cni.py /opt/cni/bin/mizarcni
RUN ln -snf /var/mizar/build/tests/mizarcni.config /etc/mizarcni.config


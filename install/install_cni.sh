#!/bin/bash

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

DIR=${1:-.}
DIR="${DIR}/mizar-k8s"

# Installing mizar cni
api_ip=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kind-control-plane`
sed "s/server: https:\/\/127.0.0.1:[[:digit:]]\+/server: https:\/\/$api_ip:6443/" ~/.kube/config > /tmp/config
docker cp /tmp/config kind-control-plane:/etc/mizarcni.config
docker cp $DIR/cni/10-mizarcni.conf kind-control-plane:/etc/cni/net.d/10-mizarcni.conf
docker cp $DIR/cni/mizarcni.py kind-control-plane:/opt/cni/bin/mizarcni.py

# Removing exisiting kind CNI
docker exec kind-control-plane rm /etc/cni/net.d/10-kindnet.conflist

# Kind image
docker exec kind-control-plane apt update
docker exec kind-control-plane apt install -y python3
docker exec kind-control-plane apt install -y python3-pip
docker exec kind-control-plane pip3 install kubernetes
docker exec kind-control-plane pip3 install pyroute2
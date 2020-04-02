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

CWD=$(pwd)
KINDCONF="${HOME}/mizar/build/tests/kind/config"
MIZARCONF="${HOME}/mizar/build/tests/mizarcni.config"
KINDHOME="${HOME}/.kube/config"
USER=${1:-user}

kind delete cluster

if [[ "$USER" == "dev" ]]; then
    DOCKER_ACC="localhost:5000"
else
    DOCKER_ACC="fwnetworking"
fi
docker image build -t $DOCKER_ACC/kindnode:latest -f k8s/kind/Dockerfile .

source install/create_cluster.sh $KINDCONF $USER

api_ip=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kind-control-plane`
sed "s/server: https:\/\/127.0.0.1:[[:digit:]]\+/server: https:\/\/$api_ip:6443/" $KINDCONF > $MIZARCONF
ln -snf $KINDCONF $KINDHOME

source install/create_crds.sh $CWD $USER
source install/create_service_account.sh $CWD $USER

source install/deploy_daemon.sh $CWD $USER $DOCKER_ACC
source install/deploy_operator.sh $CWD $USER $DOCKER_ACC
source install/disable_kubeproxy.sh $CWD $USER
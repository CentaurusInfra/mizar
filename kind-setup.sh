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

# Checks for status: Provisioned for given object
function get_status() {
    OBJECT=$1

    kubectl get $OBJECT 2> /tmp/kubetctl.err | awk '
    NR==1 {
        for (i=1; i<=NF; i++) {
            f[$i] = i
        }
    }
    { print $f["STATUS"] }
    ' | grep Provisioned > /dev/null

    return $?
}

# Checks for status Provisioned of array of objects
function check_ready() {
    objects=("droplets" "vpcs" "nets" "dividers" "bouncers")
    sum=0
    for i in "${objects[@]}"
    do
        get_status $i
        let sum+=$((sum + $?))
    done
    if [[ $sum == 0 ]]; then
        return 1
    else
        sleep 2
        echo -n "."
        return 0
    fi
}

CWD=$(pwd)
KINDCONF="${HOME}/mizar/build/tests/kind/config"
MIZARCONF="${HOME}/mizar/build/tests/mizarcni.config"
KINDHOME="${HOME}/.kube/config"
USER=${1:-user}
NODES=${2:-3}
timeout=120

kind delete cluster

if [[ "$USER" == "dev" ]]; then
    DOCKER_ACC="localhost:5000"
else
    DOCKER_ACC="fwnetworking"
fi
docker image build -t $DOCKER_ACC/kindnode:latest -f k8s/kind/Dockerfile .

source k8s/kind/create_cluster.sh $KINDCONF $USER $NODES

api_ip=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kind-control-plane`
sed "s/server: https:\/\/127.0.0.1:[[:digit:]]\+/server: https:\/\/$api_ip:6443/" $KINDCONF > $MIZARCONF
ln -snf $KINDCONF $KINDHOME

source install/create_crds.sh $CWD $USER
source install/create_service_account.sh $CWD $USER

source install/deploy_daemon.sh $CWD $USER $DOCKER_ACC
source install/deploy_operator.sh $CWD $USER $DOCKER_ACC
source install/create_testimage.sh $CWD $USER $DOCKER_ACC

end=$((SECONDS + $timeout))
echo -n "Waiting for cluster to come up."
while [[ $SECONDS -lt $end ]]; do
    check_ready || break
done
echo
if [[ $SECONDS -lt $end ]]; then
    echo "Cluster now ready!"
else
    echo "ERROR: Cluster setup timed out after $timeout seconds!"
    exit 1
fi

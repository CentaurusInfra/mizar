#!/bin/bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Hong Chang        <@Hong-Chang>
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

source install/common.sh

function environment_adaptor:prepare_binary {
    local is_mizar_production=${1:-0}

    if [[ $is_mizar_production == 0 ]]; then
        local user="dev"
    else
        local user="prod"
    fi

    local cwd=$(pwd)
    local kind_config="$cwd/build/tests/kind/config"
    local mizar_config="$cwd/build/tests/mizarcni.config"
    local kube_config="${HOME}/.kube/config"
    local nodes=${2:-3}

    kind delete cluster
    make proto

    if [[ $user == "dev" ]]; then
        local docker_account="localhost:5000"
    else
        local docker_account="fwnetworking"
    fi
    docker image build -t $docker_account/kindnode:latest -f k8s/kind/Dockerfile .

    source k8s/kind/create_cluster.sh $kind_config $user $nodes

    local api_ip=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kind-control-plane`
    sed "s/server: https:\/\/127.0.0.1:[[:digit:]]\+/server: https:\/\/$api_ip:6443/" $kind_config > $mizar_config
    ln -snf $kind_config $kube_config

    echo "Waiting for cluster to be up and running."
    local timeout=60
    common:execute_and_retry "common:check_cluster_ready 0" 1 "Cluster is up and running." "ERROR: cluster setup timed out after $timeout seconds!" $timeout 1

    # local start_time=$(date +%s)
    # local timeout=60
    # echo -n "Waiting for cluster to be ready."
    # while true; do
    #     common:check_cluster_ready 0; local is_cluster_ready=$?
    #     if [[ $is_cluster_ready == 1 ]]; then
    #         break
    #     fi
    #     sleep 2
    #     echo -n "."
    #     local elapsed=$(($(date +%s) - ${start_time}))
    #     if [[ ${elapsed} -gt $timeout ]]; then
    #         echo
    #         echo "ERROR: cluster setup timed out after $timeout seconds!"
    #         exit 1
    #     fi
    # done
}

function environment_adaptor:deploy_mizar {
    local is_mizar_production=${1:-0}

    if [[ $is_mizar_production == 0 ]]; then
        local user="dev"
    else
        local user="prod"
    fi

    local cwd=$(pwd)
    source install/create_crds.sh $cwd $user
    source install/create_service_account.sh $cwd $user

    source install/deploy_daemon.sh $cwd $user $docker_account
    source install/deploy_operator.sh $cwd $user $docker_account
    source install/create_testimage.sh $cwd $user $docker_account

    echo "Waiting for Mizar to be up and running."
    local timeout=120
    common:execute_and_retry "common:check_mizar_ready" 1 "Mizar is now ready!" "ERROR: Mizar setup timed out after $timeout seconds!" $timeout 1


    # local start_time=$(date +%s)
    # local timeout=120    
    # while true; do
    #     common:check_mizar_ready; local is_mizar_ready=$?
    #     if [[ $is_mizar_ready == 1 ]]; then
    #         break;
    #     fi
    #     sleep 2
    #     echo -n "."
    #     local elapsed=$(($(date +%s) - ${start_time}))
    #     if [[ ${elapsed} -gt $timeout ]]; then
    #         echo
    #         echo "ERROR: Mizar setup timed out after $timeout seconds!"
    #         exit 1
    #     fi
    # done
    # echo "Mizar is now ready!"
}
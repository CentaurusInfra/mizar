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

function deploy_steps:install_mizar {
    sudo cp -rf ${HOME}/mizar /var
    sudo nsenter -t 1 -m -u -n -i pip3 install --ignore-installed /var/mizar/ && \
    sudo nsenter -t 1 -m -u -n -i ln -snf /sys/fs/bpf /bpffs && \
    sudo nsenter -t 1 -m -u -n -i ln -snf /var/mizar/build/bin /trn_bin && \
    sudo nsenter -t 1 -m -u -n -i ln -snf /var/mizar/build/xdp /trn_xdp && \
    sudo nsenter -t 1 -m -u -n -i ln -snf /var/mizar/etc/cni/10-mizarcni.conf /etc/cni/net.d/10-mizarcni.conf && \
    sudo nsenter -t 1 -m -u -n -i ln -snf /var/mizar/mizar/cni.py /opt/cni/bin/mizarcni && \
    sudo nsenter -t 1 -m -u -n -i ln -snf /var/mizar/build/tests/mizarcni.config /etc/mizarcni.config && \
    echo "install-mizar-complete"
}

function deploy_steps:install_mizar_cni_in_arktos {
    sudo rm /etc/cni/net.d/bridge.conf
    deploy_steps:install_mizar
    sudo systemctl restart containerd.service
}

function deploy_steps:binaries_ready {
    local is_mizar_production=${1:-0}
    environment_adaptor:prepare_binary $is_mizar_production
}

function deploy_steps:environment_ready {
    common:check_cluster_ready; local is_cluster_ready=$?

    if [[ $is_cluster_ready == 0 ]]; then
        echo "[deploy_steps] Error: Cluster is not ready. Cannot deploy Mizar when cluster is not ready. Please make cluster up and running." 1>&2
        exit 1
    fi
}

function deploy_steps:deploy_mizar {
    local is_mizar_production=${1:-0}
    environment_adaptor:deploy_mizar $is_mizar_production
}

function deploy_steps:sanity_check {
    :
}

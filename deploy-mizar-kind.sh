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

# Parameters
MIZAR_HOME=${MIZAR_HOME:-"${HOME}/mizar"}
if [[ ! -d $MIZAR_HOME ]]; then
    echo "Error: Directory $MIZAR_HOME doesn't exist. Variable MIZAR_HOME need to be set as Mizar repository directory location." 1>&2
    exit 1
fi
source $MIZAR_HOME/install/common.sh

IS_MIZAR_PRODUCTION=${IS_MIZAR_PRODUCTION:-0}
MIZAR_ENVIRONMENT=${MIZAR_ENVIRONMENT:-"K8S_KIND"}


# Binaries ready




# Environment ready
common:check_cluster_ready; is_cluster_ready=$?

if [[ $is_cluster_ready == 0 ]]; then
    echo "Error: Cluster is not ready. Cannot deploy Mizar when cluster is not ready. Please make cluster up and running." 1>&2
    exit 1
fi




# Deploy Mizar




# Sanity Check
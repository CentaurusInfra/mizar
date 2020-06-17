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

import sys
import logging
import logging
import json
import os
from mizar.daemon.cni_service import CniClient
from mizar.proto.cni_pb2 import Pod

# 1. The pod operator will get create pod CRD event
# 2. It will create a simple endpoint (for the pod)
# 3. When the endpoint status is PROVISIONED, it will make an AddPod RPC call to
#    the host's CNI service

# simulate that the built-in POD operator data
pod = Pod(
    name='TEST',
    veth_name='veth_peer_1',
    mac="01:02:03:04:05:06",
    netns='mizar-netns-0x3473',
    ip='10.0.0.3',
    prefix='24',
    gw='10.0.0.1'
)

CniClient("localhost").AddPod(pod)

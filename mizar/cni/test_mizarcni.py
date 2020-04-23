#!/usr/bin/python3

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

import os
import subprocess
import sys
from subprocess import Popen, PIPE, STDOUT


def main():

    os.environ["CNI_COMMAND"] = 'ADD'
    os.environ["CNI_CONTAINERID"] = '320f60a0fce865a9e05a6b8e65dcb0a691d699adafe6dbf4d978b5a718ec822a'
    os.environ["CNI_NETNS"] = '/var/run/netns/cni-825fc751-3ab9-45f2-420d-2159647a0500'
    os.environ["CNI_IFNAME"] = 'eth0'
    os.environ["CNI_PATH"] = '/opt/cni/bin'
    os.environ["CNI_ARGS"] = 'IgnoreUnknown=1;K8S_POD_NAMESPACE=default;K8S_POD_NAME=hello-world2-7556f76cd-8drvm;K8S_POD_INFRA_CONTAINER_ID=320f60a0fce865a9e05a6b8e65dcb0a691d699adafe6dbf4d978b5a718ec822a'

    stdin = '{"cniVersion":"0.2.0","k8sconfig":"/tmp/config","name":"mizarcni","type":"mizarcni.py"}'

    p = Popen(['./mizarcni.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    (stdout_data, stderr_data) = p.communicate(input=stdin.encode('utf8'))

    print(stdout_data)
    print(stderr_data)


main()

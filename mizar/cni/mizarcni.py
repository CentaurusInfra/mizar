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

import subprocess
import sys
import logging
from logging.handlers import SysLogHandler
import json
import os
import fs
from mizar.common.common import *
from mizar.daemon.interface_service import InterfaceServiceClient
from mizar.proto.interface_pb2 import InterfaceId, PodId

logger = logging.getLogger('mizarcni')
logger.setLevel(logging.INFO)
handler = SysLogHandler(address='/dev/log')
logger.addHandler(handler)
logger = logging.getLogger()


class Cni:
    def __init__(self, stdin):
        stdin = ''.join(sys.stdin.readlines())
        self.command = os.environ.get("CNI_COMMAND")  # ADD | DEL | VERSION
        self.container_id = os.environ.get("CNI_CONTAINERID")
        self.netns = os.environ.get("CNI_NETNS")
        self.interface = os.environ.get("CNI_IFNAME")
        self.cni_path = os.environ.get("CNI_PATH")
        self.cni_args = os.environ.get("CNI_ARGS")

        self.cni_args_dict = dict(i.split("=")
                                  for i in self.cni_args.split(";"))
        self.k8s_namespace = self.cni_args_dict.get('K8S_POD_NAMESPACE', '')
        self.k8s_pod_name = self.cni_args_dict.get('K8S_POD_NAME', '')

        config_json = json.loads(stdin)

        # expected parameters in the CNI specification:
        self.cni_version = config_json["cniVersion"]
        self.network_name = config_json["name"]
        self.plugin = config_json["type"]

        # TODO: parse 'Arktos specific' CNI_ARGS
        self.k8s_pod_tenant = self.cni_args_dict.get('K8S_POD_TENANT', '')

        self.pod_id = PodId(
            k8s_pod_name=self.k8s_pod_name,
            k8s_namespace=self.k8s_namespace,
            k8s_pod_tenant=self.k8s_pod_tenant
        )

    def run(self):
        logging.info("CNI ARGS {}".format(self.cni_args_dict))
        val = "Unsuported cni command!"
        switcher = {
            'ADD': self.do_add,
            'DEL': self.do_delete,
            'GET': self.do_get,
            'VERSION': self.do_version
        }

        func = switcher.get(self.command, lambda: "Unsuported cni command")
        if func:
            func()
        print(val)
        exit(1)

    def do_add(self):
        val, status = conn.root.add(params)
        logger.info("server's add is {} {}".format(val, status))
        print(val)
        exit(status)

    def do_delete(self):
        logger.info("Delete called")
        exit(1)

    def do_get(self):
        logger.info("server's get is {}".format(val))
        print("")
        exit(0)

    def do_version(self):
        val, status = json.dumps({'cniVersion': '0.3.1', "supportedVersions": [
            "0.2.0", "0.3.0", "0.3.1"]}), 0
        logger.info("server's version is {}".format(val))
        print(val)
        exit(status)


params = CniParameters(
    pod_id=PodId(
        k8s_pod_name=cniparams.k8s_pod_name,
        k8s_namespace=cniparams.k8s_namespace,
        k8s_pod_tenant=cniparams.k8s_pod_tenant
    ),
    command=cniparams.command,
    container_id=cniparams.container_id,
    netns=cniparams.netns,
    interface=cniparams.interface,
    cni_version=cniparams.cni_version
)

mem_fs = fs.open_fs('mem://')

logger.info("Invoke CNI with params: {}".format(params))
results = CniClient("localhost").Cni(params)
logger.info("CNI results: {}".format(results))

# The result is given in the result_string
if results.value != CniResultsValue.file_pending:
    print(results.result_string)
    results.value == CniResultsValue.string_success and exit(0)
    exit(1)

# Wait for file in results.result_file_path
while not mem_fs.exists(results.result_file_path):
    pass

with mem_fs.open(results.result_file_path) as f:
    results_file = json.load(f)

print(results_file['result'])
if results_file['status'] == 'success':
    exit(0)
exit(1)


cni = Cni()
cni.run()

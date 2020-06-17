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
import json
import subprocess
import logging

logger = logging.getLogger()

# parser for the CNI env and stdin as is, without any post-processing


class CniParams:
    def __init__(self, stdin):
        self.command = os.environ.get("CNI_COMMAND")  # ADD | DEL | VERSION
        self.container_id = os.environ.get("CNI_CONTAINERID")
        self.netns = os.environ.get("CNI_NETNS")
        self.interface = os.environ.get("CNI_IFNAME")
        self.cni_path = os.environ.get("CNI_PATH")
        self.cni_args = os.environ.get("CNI_ARGS")

        self.cni_args_dict = dict(i.split("=")
                                  for i in self.cni_args.split(";"))
        self.k8s_namespace = self.cni_args_dict.get('K8S_POD_NAMESPACE', None)
        self.k8s_pod_name = self.cni_args_dict.get('K8S_POD_NAME', None)

        # TODO: parse 'Arktos specific' CNI_ARGS

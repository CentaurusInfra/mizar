# SPDX-License-Identifier: MIT
# Copyright (c) 2022 The Authors.

# Authors: The Mizar Team

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

import logging
import sys
import os
import subprocess
import mizar.proto.droplet_pb2 as droplet_pb2
import mizar.proto.droplet_pb2_grpc as droplet_pb2_grpc
import time
import grpc
from concurrent import futures
from google.protobuf import empty_pb2
from mizar.common.common import get_itf
from mizar.common.constants import OBJ_DEFAULTS

logger = logging.getLogger()


class DropletServer(droplet_pb2_grpc.DropletServiceServicer):

    def __init__(self):
        self.itf = get_itf()
        cmd = 'ip addr show %s | grep "inet\\b" | awk \'{print $2}\' | cut -d/ -f1' % self.itf
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.ip = r.stdout.read().decode().strip()

        cmd = 'ip addr show ' + f'''{self.itf}''' + ' | grep "link/ether\\b" | awk \'{print $2}\' | cut -d/ -f1'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.mac = r.stdout.read().decode().strip()

        cmd = 'hostname'
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        self.name = r.stdout.read().decode().strip()

        # Disable TSO and checksum offload as xdp currently does not support
        cmd = "ethtool -K {} tso off gso off ufo off".format(self.itf)
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        cmd = "ethtool --offload {} rx off tx off".format(self.itf)
        r = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    def GetDropletInfo(self, request, context):
        droplet = droplet_pb2.Droplet(
            name=self.name,
            ip=self.ip,
            mac=self.mac,
            itf=self.itf
        )
        return droplet


class DropletClient():
    def __init__(self, ip):
        addr = '{}:{}'.format(ip, OBJ_DEFAULTS.mizar_daemon_service_port)
        self.channel = grpc.insecure_channel(addr)
        self.stub = droplet_pb2_grpc.DropletServiceStub(self.channel)

    def GetDropletInfo(self):
        resp = self.stub.GetDropletInfo(empty_pb2.Empty())
        return resp

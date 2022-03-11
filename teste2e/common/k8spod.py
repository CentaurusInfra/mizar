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

from teste2e.common.helper import *
from time import sleep

SCRIPTS_DIR = '/var/mizar/test/scripts'


class k8sPod:

    def __init__(self, api, name, ip):
        self.api = api
        self.name = name
        self.ip = ip

    @property
    def eptype(self):
        return "simple"

    def do_ping(self, server, count=1, wait=5):
        ip = server.ip
        cmd = 'ping -w {} -c {} {}'.format(wait, count, ip)
        err = self.api.pod_exec(self.name, cmd)
        logger.info("do_ping output {}, got: {}".format(self.name, err))
        return err['status'] == "Success"

    def do_curl_hostname(self, server, ep_type="simple"):
        ip = server.ip
        cmd = f'''/bin/bash {SCRIPTS_DIR}/curl_client_hostname.sh {ip} {ep_type}'''
        out = self.api.pod_exec_stdout(self.name, cmd)
        logger.info("do_curl_client {}, got: {}".format(self.name, out))

        if server.eptype == "simple":
            return out == server.name

        if server.eptype == "scaled":
            return out in server.backends

    def do_tcp_hostname(self, server, ep_type="simple"):
        ip = server.ip
        cmd = f'''/bin/bash {SCRIPTS_DIR}/nc_client_hostname.sh {ip} tcp {ep_type}'''
        out = self.api.pod_exec_stdout(self.name, cmd)
        logger.info("do_tcp_client {}, got: {}".format(self.name, out))

        if server.eptype == "simple":
            return out == server.name

        if server.eptype == "scaled":
            return out in server.backends

    def do_udp_hostname(self, server, ep_type="simple"):
        ip = server.ip
        cmd = f'''/bin/bash {SCRIPTS_DIR}/nc_client_hostname.sh {ip} udp {ep_type}'''
        out = self.api.pod_exec_stdout(self.name, cmd)
        logger.info("do_udp_client {}, got: {}".format(self.name, out))

        if server.eptype == "simple":
            return out == server.name

        if server.eptype == "scaled":
            return out in server.backends

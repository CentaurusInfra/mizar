# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Hong Chang        <@Hong-Chang>

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
from mizar.common.common import *

class Network(object):
    def __init__(self, name, obj_api, opr_store, vpcId, tenant, resourceVersion):
        self.name = name
        self.obj_api = obj_api
        self.store = opr_store
        self.vpcId = vpcId
        self.tenant = tenant
        self.resourceVersion = resourceVersion

        self.phase = ""
        self.message = ""
        self.dnsServiceIP = ""

    def get_obj_spec(self):
        return {
            "apiVersion": "{0}/{1}".format(self.get_group(), self.get_version()),
            "kind": self.get_kind(),
            "metadata": {
                "name": self.name,
                "resourceVersion": self.resourceVersion
            },
            "status": {
                "phase": self.phase,
                "message": self.message,
                "dnsServiceIP": self.dnsServiceIP
            }
        }

    def get_name(self):
        return self.name

    def get_vpcId(self):
        return self.vpcId

    def get_plural(self):
        return "networks"

    def get_kind(self):
        return "Network"

    def store_update_obj(self):
        if self.store is None:
            return
        self.store.update_network(self) # todo hochan implement

    def store_delete_obj(self):
        if self.store is None:
            return
        self.store.delete_network(self.name) # todo hochan implement

    def get_group(self):
        return "arktos.futurewei.com"

    def get_version(self):
        return "v1"

    def get_tenant(self):
        return self.tenant

    def get_resourceVersion(self):
        return self.resourceVersion

    def set_status(self, resourceVersion):
        self.resourceVersion = resourceVersion

    def get_status(self):
        return '{{"phase":"{0}", "message":"{1}", "dnsServiceIP":"{2}"}}'.format(
                self.phase,
                self.message,
                self.dnsServiceIP
            )

    def set_status(self, phase=None, message=None, dnsServiceIP=None):
        if phase is not None:
            self.phase = phase
        if message is not None:
            self.message = message
        if dnsServiceIP is not None:
            self.dnsServiceIP = dnsServiceIP

    def update_status(self):
        return kube_update_tenant_obj_status(self)
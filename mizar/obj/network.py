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
    def __init__(self, name, obj_api, opr_store, body):
        self.name = name
        self.obj_api = obj_api
        self.store = opr_store
        self.vpcName = body['spec']['vpcID']
        self.tenant = body['metadata']['tenant']
        self.resourceVersion = body['metadata']['resourceVersion']

        self.phase = ""
        self.message = ""
        self.dnsServiceIP = ""
    
    def get_name(self):
        return self.name

    def get_vpcName(self):
        return self.vpcName

    def get_plural(self):
        return "networks"

    def get_kind(self):
        return "Network"
    
    def get_group(self):
        return "arktos.futurewei.com"

    def get_version(self):
        return "v1"

    def get_tenant(self):
        return self.tenant

    def get_resourceVersion(self):
        return self.resourceVersion

    def set_resourceVersion(self, resourceVersion):
        self.resourceVersion = resourceVersion

    def get_phase(self):
        return self.phase

    def set_phase(self, phase):
        self.phase = phase

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message

    def get_dnsServiceIP(self):
        return self.dnsServiceIP

    def set_dnsServiceIP(self, dnsServiceIP):
        self.dnsServiceIP = dnsServiceIP

    def store_update_obj(self):
        if self.store is None:
            return
        self.store.update_network(self)

    def store_delete_obj(self):
        if self.store is None:
            return
        self.store.delete_network(self.name)

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

    def update_status(self):
        return kube_update_tenant_obj_status(self)
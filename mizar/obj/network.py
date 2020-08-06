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
    def __init__(self, name, obj_api, body):
        self.name = name
        self.obj_api = obj_api
        self.body = body
        self.message = ""

    def get_name(self):
        return self.name

    def get_plural(self):
        return "networks"

    def get_kind(self):
        return "Network"

    def get_group(self):
        return "arktos.futurewei.com"

    def get_version(self):
        return "v1"

    def set_message(self, message):
        self.message = message

    def update_obj(self):
        return kube_update_cluster_obj(self)
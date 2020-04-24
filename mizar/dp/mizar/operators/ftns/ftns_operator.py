# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>
#          Cathy Lu          <@clu2>

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

import random
import logging
from kubernetes import client, config
from common.constants import *
from common.common import *
from obj.ftn import Ftn
from store.operator_store import OprStore

logger = logging.getLogger()

class FtnOperator(object):
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(FtnOperator, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self, **kwargs):
		logger.info(kwargs)
		self.store = OprStore()
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def query_existing_ftns(self):
		logger.info("ftns on_startup")
		def list_ftns_obj_fn(name, spec, plurals):
			logger.info("Bootstrapped Ftn {}".format(name))
			f = Ftn(self.obj_api, self.store, spec)
			self.store_update(f)

		kube_list_obj(self.obj_api, RESOURCES.droplets, list_ftns_obj_fn)

	def get_ftn_stored_obj(self, name, spec):
		return Ftn(self.obj_api, self.store, spec)

	def create_default_ftn(self):
		if self.store.get_ftn():
			return
		f = Ftn(self.obj_api, self.store)
		f.create_obj()

	def store_update(self, b):
		self.store.update_ftn(b)

	def set_ftn_provisioned(self, ftn):
		ftn.set_status(OBJ_STATUS.ftn_status_provisioned)
		ftn.update_obj()

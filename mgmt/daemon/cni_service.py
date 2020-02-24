import os
import sys
import json
import logging
import uuid
import pprint
import subprocess
from rpyc import Service
from socket import AF_INET
from pyroute2 import IPRoute, NetNS
from kubernetes import client, config, watch

logger = logging.getLogger()

class CniService(Service):

	def __init__(self):
		config.load_incluster_config()
		self.obj_api = client.CustomObjectsApi()

	def exposed_add(self, params):
		val = "!!add service!!"
		status = 1
		logger.info("cni service add {}".format(params))
		return val, status

	def exposed_delete(self, params):
		val = "!!delete service!!"
		status = 1
		logger.info("cni service delete {}".format(params))
		return val, status

	def exposed_get(self, params):
		val = "!!get service!!"
		status = 1
		logger.info("cni service get {}".format(params))
		return val, status

	def exposed_version(self, params):
		val = "!!version service!!"
		status = 1
		logger.info("cni service version {}".format(params))
		return val, status
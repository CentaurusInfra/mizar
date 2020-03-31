from common import *
from cli.mizarapi import  *
from kubernetes import client, config

class k8sCluster:
	_instance = None

	def __new__(cls, **kwargs):
		if cls._instance is None:
			cls._instance = super(k8sCluster, cls).__new__(cls)
			cls._init(cls, **kwargs)
		return cls._instance

	def _init(self):
		logger.info("Check or start existing cluster")
		if not self.is_running(self):
			self.start_cluster(self)
		else:
			logger.info("Test cluster is already running")

	def start_cluster(self):
		logger.info("Start test cluster")
		run_cmd("./kind-setup.sh")

	def is_running(self):
		ret, val = run_cmd("kind get clusters")
		return val.strip() == TEST_CLUSTER

	def delete_cluster(self):
		logger.info("Delete test cluster")
		run_cmd("kind delete cluster")


class k8sApi:

	def __init__(self):
		self.api = MizarApi()

	def create_vpc(self, name, ip, prefix, dividers=1, vni=None):
		self.api.create_vpc(name, ip, prefix, dividers, vni)


	def delete_vpc(self, name):
		self.api.delete_vpc(name)
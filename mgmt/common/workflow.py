from __future__ import annotations
import luigi
from abc import ABC, abstractmethod
from common.wf_param import *

class WorkflowTask(luigi.Task):
	is_complete = False
	param = HandlerParam()

	def finalize(self):
		self.is_complete = True

	def complete(self):
		return self.is_complete

	def requires(self):
		return []

	def run(self):
		self.finalize()

class WorkflowFactory(ABC):

	@abstractmethod
	def VpcOperatorStart(self, param):
		pass

	@abstractmethod
	def VpcCreate(self, param):
		pass

	@abstractmethod
	def VpcProvisioned(self, param):
		pass

	@abstractmethod
	def DividerOperatorStart(self, param):
		pass

	@abstractmethod
	def DividerCreate(self, param):
		pass

	@abstractmethod
	def DividerProvisioned(self, param):
		pass

	@abstractmethod
	def DropletOperatorStart(self, param):
		pass

	@abstractmethod
	def DropletCreate(self, param):
		pass

	@abstractmethod
	def DropletProvisioned(self, param):
		pass

	@abstractmethod
	def NetOperatorStart(self, param):
		pass

	@abstractmethod
	def NetCreate(self, param):
		pass

	@abstractmethod
	def NetProvisioned(self, param):
		pass

	@abstractmethod
	def BouncerOperatorStart(self, param):
		pass

	@abstractmethod
	def BouncerCreate(self, param):
		pass

	@abstractmethod
	def BouncerProvisioned(self, param):
		pass

	@abstractmethod
	def k8sServiceCreate(self, param):
		pass

	@abstractmethod
	def k8sEndpointsUpdate(self, param):
		pass

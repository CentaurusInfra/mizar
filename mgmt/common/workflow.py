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




import luigi
from common.workflow import *
from operators.vpcs.workflows.bootstrap import *
from operators.vpcs.workflows.create import *
from operators.vpcs.workflows.provisioned import *
from operators.vpcs.workflows.delete import *

class MizarWorkflowFactory():

	def VpcOperatorStart(self, param):
		return VpcOperatorStart(param=param)

	def VpcCreate(self, param):
		return VpcCreate(param=param)

	def VpcProvisioned(self, param):
		return VpcProvisioned(param=param)
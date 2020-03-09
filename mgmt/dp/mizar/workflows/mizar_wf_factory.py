import luigi
from common.workflow import *
from dp.mizar.workflows.vpcs.bootstrap import *
from dp.mizar.workflows.vpcs.create import *
from dp.mizar.workflows.vpcs.provisioned import *
from dp.mizar.workflows.vpcs.delete import *

from dp.mizar.workflows.dividers.bootstrap import *
from dp.mizar.workflows.dividers.create import *
from dp.mizar.workflows.dividers.provisioned import *
from dp.mizar.workflows.dividers.delete import *

class MizarWorkflowFactory():

	def VpcOperatorStart(self, param):
		return VpcOperatorStart(param=param)

	def VpcCreate(self, param):
		return VpcCreate(param=param)

	def VpcProvisioned(self, param):
		return VpcProvisioned(param=param)

	def DividerOperatorStart(self, param):
		return DividerOperatorStart(param=param)

	def DividerCreate(self, param):
		return DividerCreate(param=param)

	def DividerProvisioned(self, param):
		return DividerProvisioned(param=param)
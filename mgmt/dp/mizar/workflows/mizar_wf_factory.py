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

from dp.mizar.workflows.droplets.bootstrap import *
from dp.mizar.workflows.droplets.create import *
from dp.mizar.workflows.droplets.provisioned import *
from dp.mizar.workflows.droplets.delete import *

from dp.mizar.workflows.nets.bootstrap import *
from dp.mizar.workflows.nets.create import *
from dp.mizar.workflows.nets.provisioned import *
from dp.mizar.workflows.nets.delete import *

from dp.mizar.workflows.bouncers.bootstrap import *
from dp.mizar.workflows.bouncers.create import *
from dp.mizar.workflows.bouncers.provisioned import *
from dp.mizar.workflows.bouncers.delete import *

from dp.mizar.workflows.endpoints.bootstrap import *
from dp.mizar.workflows.endpoints.create import *
from dp.mizar.workflows.endpoints.provisioned import *
from dp.mizar.workflows.endpoints.delete import *

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

	def DropletOperatorStart(self, param):
		return DropletOperatorStart(param=param)

	def DropletCreate(self, param):
		return DropletCreate(param=param)

	def DropletProvisioned(self, param):
		return DropletProvisioned(param=param)

	def NetOperatorStart(self, param):
		return NetOperatorStart(param=param)

	def NetCreate(self, param):
		return NetCreate(param=param)

	def NetProvisioned(self, param):
		return NetProvisioned(param=param)

	def BouncerOperatorStart(self, param):
		return BouncerOperatorStart(param=param)

	def BouncerCreate(self, param):
		return BouncerCreate(param=param)

	def BouncerProvisioned(self, param):
		return BouncerProvisioned(param=param)

	def EndpointOperatorStart(self, param):
		return EndpointOperatorStart(param=param)

	def EndpointCreate(self, param):
		return EndpointCreate(param=param)

	def EndpointProvisioned(self, param):
		return EndpointProvisioned(param=param)
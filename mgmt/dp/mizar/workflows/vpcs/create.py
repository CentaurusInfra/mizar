import logging
from common.workflow import *
from dp.mizar.operators.vpcs.vpcs_operator import *
logger = logging.getLogger()

vpcs_opr = VpcOperator()

class VpcAllocateVNI(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		v = vpcs_opr.get_vpc_tmp_obj(self.param.name, self.param.spec)
		vpcs_opr.allocate_vni(v)
		self.finalize()

class VpcCreateDividers(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return [VpcAllocateVNI(param=self.param)]

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		v = vpcs_opr.get_vpc_tmp_obj(self.param.name, self.param.spec)
		vpcs_opr.create_vpc_dividers(v)
		self.finalize()

class VpcCreate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return [VpcCreateDividers(param=self.param)]

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		v = vpcs_opr.get_vpc_stored_obj(self.param.name, self.param.spec)
		vpcs_opr.set_vpc_provisioned(v)
		self.finalize()
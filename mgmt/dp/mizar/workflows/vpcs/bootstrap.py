import logging
from common.workflow import *
from dp.mizar.operators.vpcs.vpcs_operator import *
from time import sleep
logger = logging.getLogger()

vpcs_opr = VpcOperator()

class VpcOperatorStart(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		sleep(2)
		vpcs_opr.query_existing_vpcs()
		vpcs_opr.create_default_vpc()
		self.finalize()
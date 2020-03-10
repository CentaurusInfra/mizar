import logging
from common.workflow import *
from dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

nets_opr = NetOperator()

class NetOperatorStart(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		nets_opr.query_existing_nets()
		nets_opr.create_default_net()
		self.finalize()
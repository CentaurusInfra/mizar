import logging
from common.workflow import *
from dp.mizar.operators.droplets.droplets_operator import *
logger = logging.getLogger()

droplets_opr = DropletOperator()

class DropletOperatorStart(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		droplets_opr.query_existing_droplets()
		self.finalize()
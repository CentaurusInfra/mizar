import logging
from common.workflow import *
from dp.mizar.operators.endpoints.endpoints_operator import *
logger = logging.getLogger()

endpoints_opr = EndpointOperator()

class EndpointOperatorStart(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		endpoints_opr.query_existing_endpoints()
		self.finalize()
import logging
from common.workflow import *
from dp.mizar.operators.endpoints.endpoints_operator import *

logger = logging.getLogger()

endpoints_opr = EndpointOperator()

class EndpointProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		endpoints_opr.store.get_ep(self.param.name).set_obj_spec(self.param.spec)
		self.finalize()
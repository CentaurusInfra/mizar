import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *

logger = logging.getLogger()

dividers_opr = DividerOperator()

class DividerProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		dividers_opr.store.get_divider(self.param.name).set_obj_spec(self.param.spec)
		self.finalize()
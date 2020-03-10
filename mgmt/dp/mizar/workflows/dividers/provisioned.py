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
		divider = dividers_opr.get_divider_stored_obj(self.param.name, self.param.spec)
		dividers_opr.store_update(divider)
		self.finalize()
import logging
from common.workflow import *
from dp.mizar.operators.bouncers.bouncers_operator import *
logger = logging.getLogger()

bouncers_opr = BouncerOperator()
class BouncerProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		bouncers_opr.store.get_bouncer(self.param.name).set_obj_spec(self.param.spec)
		self.finalize()
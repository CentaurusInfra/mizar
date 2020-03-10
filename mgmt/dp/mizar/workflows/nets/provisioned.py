import logging
from common.workflow import *
from dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

nets_opr = NetOperator()

class NetProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		n = nets_opr.get_net_stored_obj(self.param.name, self.param.spec)
		nets_opr.store_update(n)
		self.finalize()
import logging
from common.workflow import *
from dp.mizar.operators.droplets.droplets_operator import *
logger = logging.getLogger()

droplets_opr = DropletOperator()

class DropletProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		d = droplets_opr.get_droplet_stored_obj(self.param.name, self.param.spec)
		droplets_opr.store_update(d)
		self.finalize()
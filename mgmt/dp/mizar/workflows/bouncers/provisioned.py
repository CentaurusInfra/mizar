import logging
from common.workflow import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.droplets.droplets_operator import *
logger = logging.getLogger()

bouncers_opr = BouncerOperator()
droplets_opr = DropletOperator()
class BouncerProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		bouncer = bouncers_opr.get_bouncer_stored_obj(self.param.name, self.param.spec)
		bouncer.droplet_obj = droplets_opr.store.get_droplet(bouncer.droplet)
		bouncers_opr.store_update(bouncer)
		self.finalize()
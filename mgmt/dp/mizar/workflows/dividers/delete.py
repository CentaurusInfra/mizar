import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.droplets.droplets_operator import *

logger = logging.getLogger()

dividers_opr = DividerOperator()
bouncers_opr = BouncerOperator()
droplets_opr = DropletOperator()

class DividerDelete(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		divider = dividers_opr.get_divider_stored_obj(self.param.name, self.param.spec)
		divider.droplet_obj = droplets_opr.store.get_droplet(divider.droplet)

		# Call delete_net on divider droplet
		# Call delete_substrate on divider droplet for all bouncer droplets

		# Call update_vpc on all bouncer droplets
		# Call delete_substrate of divider droplet on all bouncer droplets
		bouncers_opr.delete_bouncers_from_divider(divider)
		self.finalize()
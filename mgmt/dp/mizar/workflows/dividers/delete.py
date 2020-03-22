import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *

logger = logging.getLogger()

dividers_opr = DividerOperator()
bouncers_opr = BouncerOperator()

class DividerDelete(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		divider = dividers_opr.store.get_divider(self.param.name)
		divider.set_obj_spec(self.param.spec)

		# Call delete_net on divider droplet
		# Call delete_substrate on divider droplet for all bouncer droplets
		dividers_opr.delete_net()

		# Call update_vpc on all bouncer droplets
		# Call delete_substrate of divider droplet on all bouncer droplets
		bouncers_opr.delete_divider_from_bouncers(divider)

		self.finalize()
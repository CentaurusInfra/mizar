import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.nets.nets_operator import *

logger = logging.getLogger()

dividers_opr = DividerOperator()
bouncers_opr = BouncerOperator()
nets_opr = NetOperator()

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
		nets = nets_opr.store.get_nets_in_vpc(divider.vpc).values()
		dividers_opr.delete_nets_from_divider(nets, divider)

		# Call update_vpc on all bouncer droplets
		# Call delete_substrate of divider droplet on all bouncer droplets
		bouncers_opr.delete_divider_from_bouncers(divider)
		divider.delete_obj()
		dividers_opr.store.delete_divider(divider.name)
		self.finalize()
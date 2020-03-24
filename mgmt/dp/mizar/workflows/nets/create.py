import logging
from common.workflow import *
from dp.mizar.operators.nets.nets_operator import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *

logger = logging.getLogger()

nets_opr = NetOperator()
dividers_opr = DividerOperator()
bouncers_opr = BouncerOperator()

class NetCreate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		n = nets_opr.get_net_stored_obj(self.param.name, self.param.spec)

		while len(dividers_opr.store.get_dividers_of_vpc(n.vpc)) < 1:
			pass

		nets_opr.create_net_bouncers(n, n.n_bouncers)
		nets_opr.set_net_provisioned(n)
		nets_opr.store_update(n)
		self.finalize()
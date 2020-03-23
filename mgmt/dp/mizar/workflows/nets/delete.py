import logging
from common.workflow import *
from dp.mizar.operators.nets.nets_operator import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
logger = logging.getLogger()

nets_opr = NetOperator()
dividers_opr = DividerOperator()
bouncers_opr = BouncerOperator()

class NetDelete(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		n = nets_opr.store.get_net(self.param.name)
		n.set_obj_spec(self.param.spec)
		nets_opr.delete_net_bouncers(n, n.n_bouncers)
		while len(bouncers_opr.store.get_bouncers_of_net(n.name)) > 1:
			pass
		dividers_opr.delete_net(n)
		nets_opr.store.delete_net(n.name)
		self.finalize()
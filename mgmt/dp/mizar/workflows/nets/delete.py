import logging
from common.workflow import *
from dp.mizar.operators.nets.nets_operator import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.endpoints.endpoints_operator import *
logger = logging.getLogger()

nets_opr = NetOperator()
dividers_opr = DividerOperator()
bouncers_opr = BouncerOperator()
endpoints_opr = EndpointOperator()

class NetDelete(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		n = nets_opr.store.get_net(self.param.name)
		n.set_obj_spec(self.param.spec)
		# TODO: Handle the error when all endpoints have not been deleted.
		while len(endpoints_opr.store.get_eps_in_net(n.name)):
			pass

		nets_opr.delete_net_bouncers(n, n.n_bouncers)
		while len(bouncers_opr.store.get_bouncers_of_net(n.name)) > 1:
			pass
		dividers_opr.delete_net(n)
		n.delete_obj()
		nets_opr.store.delete_net(n.name)
		self.finalize()

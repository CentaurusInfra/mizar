import logging
from common.workflow import *

from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.endpoints.endpoints_operator import *
from dp.mizar.operators.nets.nets_operator import *

logger = logging.getLogger()

bouncers_opr = BouncerOperator()
endpoints_opr = EndpointOperator()
nets_opr = NetOperator()

class EndpointDelete(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		ep = endpoints_opr.store.get_ep(self.param.name)
		ep.set_obj_spec(self.param.spec)
		nets_opr.deallocate_endpoint(ep)
		bouncers_opr.delete_endpoint_from_bouncers(ep)
		endpoints_opr.set_endpoint_deprovisioned(ep)
		endpoints_opr.store.delete_ep(ep.name)
		self.finalize()

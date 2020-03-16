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
		ep = endpoints_opr.get_endpoint_stored_obj(self.param.name, self.param.spec)
		nets_opr.deallocate_endpoint(ep)
		bouncers_opr.delete_endpoint_with_bouncers(ep)
		endpoints_opr.set_endpoint_deprovisioned(ep)
		self.finalize()

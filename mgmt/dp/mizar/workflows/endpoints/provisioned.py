import logging
from common.workflow import *
from dp.mizar.operators.endpoints.endpoints_operator import *
from dp.mizar.operators.droplets.droplets_operator import *

logger = logging.getLogger()

endpoints_opr = EndpointOperator()
droplets_opr = DropletOperator()

class EndpointProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		ep = endpoints_opr.get_endpoint_stored_obj(self.param.name, self.param.spec)
		ep.droplet_obj = droplets_opr.store.get_droplet(ep.droplet)
		endpoints_opr.store_update(ep)
		self.finalize()
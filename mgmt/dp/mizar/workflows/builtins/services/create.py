import logging
from common.workflow import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.endpoints.endpoints_operator import *
from dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

endpoints_opr = EndpointOperator()
bouncers_opr = BouncerOperator()

class k8sServiceCreate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		endpoints_opr.create_scaled_endpoint(self.param.name, self.param.spec)
		self.finalize()


class k8sEndpointsUpdate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		if 'subsets' not in self.param.body:
			return
		ep = endpoints_opr.update_scaled_endpoint_backend(self.param.name, self.param.body['subsets'])
		if ep:
			bouncers_opr.update_endpoint_with_bouncers(ep)
		self.finalize()
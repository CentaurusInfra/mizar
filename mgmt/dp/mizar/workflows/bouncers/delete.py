import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.endpoints.endpoints_operator import *
from dp.mizar.operators.nets.nets_operator import *

logger = logging.getLogger()

dividers_opr = DividerOperator()
bouncers_opr = BouncerOperator()
endpoints_opr = EndpointOperator()
nets_opr = NetOperator()

class BouncerDelete(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		bouncer = bouncers_opr.store.get_bouncer(self.param.name)
		bouncer.set_obj_spec(self.param.spec)
		net = nets_opr.store.get_net(bouncer.net)
		# Call update_net on all divider objects
		# Call delete_substrate of bouncer droplet on all divider droplets

		# Call delete_ep on bouncer droplet for all endpoints
		# Call update_agent on all endpoints with new list of bouncers
		endpoints_opr.delete_bouncer_from_endpoints(bouncer)
		dividers_opr.delete_bouncer_from_dividers(bouncer, net)
		endpoints_opr.delete_endpoints_from_bouncers(bouncer)
		bouncers_opr.delete_vpc(bouncer)
		bouncer.delete_obj()
		bouncers_opr.store.delete_bouncer(bouncer.name)
		self.finalize()
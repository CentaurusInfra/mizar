import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.droplets.droplets_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.endpoints.endpoints_operator import *
from dp.mizar.operators.nets.nets_operator import *
from dp.mizar.operators.vpcs.vpcs_operator import *

logger = logging.getLogger()

dividers_opr = DividerOperator()
droplets_opr = DropletOperator()
bouncers_opr = BouncerOperator()
endpoints_opr = EndpointOperator()
nets_opr = NetOperator()
vpcs_opr = VpcOperator()

logger = logging.getLogger()
class BouncerCreate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		bouncer = bouncers_opr.get_bouncer_stored_obj(self.param.name, self.param.spec)
		while not droplets_opr.is_bootstrapped():
			pass

		droplets_opr.assign_bouncer_droplet(bouncer)

		# Update vpc on bouncer
		# Needs a list of all dividers
		bouncer.set_vni(vpcs_opr.store.get_vpc(bouncer.vpc).vni)
		dividers_opr.update_vpc(bouncer)

		endpoints_opr.update_bouncer_with_endpoints(bouncer)
		endpoints_opr.update_endpoints_with_bouncers(bouncer)

		# Update net on dividers
		net = nets_opr.store.get_net(bouncer.net)
		if net:
			net.bouncers[bouncer.name] = bouncer
			dividers_opr.update_divider_with_bouncers(bouncer, net)

		bouncers_opr.set_bouncer_provisioned(bouncer)
		bouncers_opr.store.update_bouncer(bouncer)
		self.finalize()
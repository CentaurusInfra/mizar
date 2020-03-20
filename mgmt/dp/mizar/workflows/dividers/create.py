import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.droplets.droplets_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
from dp.mizar.operators.vpcs.vpcs_operator import *
logger = logging.getLogger()

dividers_opr = DividerOperator()
droplets_opr = DropletOperator()
bouncers_opr = BouncerOperator()
vpcs_opr = VpcOperator()

class DividerCreate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		divider = dividers_opr.get_divider_stored_obj(self.param.name, self.param.spec)
		while not droplets_opr.is_bootstrapped():
			pass

		droplets_opr.assign_divider_droplet(divider)

		logger.info("GET NAME " + divider.droplet_obj.get_name())

		# Update vpc on bouncers
		bouncers_opr.update_bouncers_with_divider(divider)

		# Update net on divider
		vpc = vpcs_opr.store.get_vpc(divider.vpc)
		divider.vpc = vpc.name
		logger.info("Len of nets is {}".format(len(vpc.networks.values())))
		for net in vpc.networks.values():
			dividers_opr.update_net(net, set([divider]))

		dividers_opr.set_divider_provisioned(divider)
		self.finalize()
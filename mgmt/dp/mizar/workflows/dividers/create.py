import logging
from common.workflow import *
from dp.mizar.operators.dividers.dividers_operator import *
from dp.mizar.operators.droplets.droplets_operator import *
from dp.mizar.operators.bouncers.bouncers_operator import *
logger = logging.getLogger()

dividers_opr = DividerOperator()
droplets_opr = DropletOperator()
bouncers_opr = BouncerOperator()

class DividerPlace(WorkflowTask):
	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("!!Run {task}".format(task=self.__class__.__name__))
		d = dividers_opr.get_divider_stored_obj(self.param.name, self.param.spec)
		droplets_opr.assign_divider_droplet(d)
		self.finalize()

class DividerUpdateBouncers(WorkflowTask):
	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return [DividerPlace(param=self.param)]

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		d = dividers_opr.get_divider_stored_obj(self.param.name, self.param.spec)
		bouncers_opr.update_bouncers_with_divider(d)
		self.finalize()

class DividerCreate(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return [DividerUpdateBouncers(param=self.param)]

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		d = dividers_opr.get_divider_stored_obj(self.param.name, self.param.spec)
		dividers_opr.set_divider_provisioned(d)
		self.finalize()
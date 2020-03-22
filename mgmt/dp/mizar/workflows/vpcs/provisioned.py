import logging
from common.workflow import *
from dp.mizar.operators.vpcs.vpcs_operator import *
logger = logging.getLogger()

vpcs_opr = VpcOperator()

class VpcProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		v = vpcs_opr.store.get_vpc(self.param.name)
		v.set_obj_spec(self.param.spec)
		for d in self.param.diff:
			if d[0] == 'change':
				self.process_change(vpc=v, field=d[1], old=d[2], new=d[3])
		vpcs_opr.store_update(v)
		self.finalize()

	def process_change(self, vpc, field, old, new):
		logger.info("diff_field:{}, from:{}, to:{}".format(field, old, new))
		if field[0] == 'spec' and field[1] == 'dividers':
			return vpcs_opr.process_divider_change(vpc, int(old), int(new))
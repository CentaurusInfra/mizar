import logging
from common.workflow import *
from dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

nets_opr = NetOperator()

class NetProvisioned(WorkflowTask):

	def requires(self):
		logger.info("Requires {task}".format(task=self.__class__.__name__))
		return []

	def run(self):
		logger.info("Run {task}".format(task=self.__class__.__name__))
		n = nets_opr.store.get_net(self.param.name)
		n.set_obj_spec(self.param.spec)
		for d in self.param.diff:
			if d[0] == 'change':
				self.process_change(net=n, field=d[1], old=d[2], new=d[3])
		nets_opr.store_update(n)
		self.finalize()

	def process_change(self, net, field, old, new):
		logger.info("diff_field:{}, from:{}, to:{}".format(field, old, new))
		if field[0] == 'spec' and field[1] == 'bouncers':
			return nets_opr.process_bouncer_change(net, int(old), int(new))
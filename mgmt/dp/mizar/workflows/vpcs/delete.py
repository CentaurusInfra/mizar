import logging
from common.workflow import *
from dp.mizar.operators.vpcs.vpcs_operator import *
logger = logging.getLogger()

vpcs_opr = VpcOperator()

class VpcDelete(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        v = vpcs_opr.get_vpc_stored_obj(self.param.name, self.param.spec)
        if len(v.networks) > 0:
            self.finalize()
            return
        vpcs_opr.deallocate_vni(v)
        vpcs_opr.delete_vpc_dividers(v, v.n_dividers)
        self.finalize()
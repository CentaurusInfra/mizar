import logging
from common.workflow import *
from dp.mizar.operators.vpcs.vpcs_operator import *
from dp.mizar.operators.nets.nets_operator import *
logger = logging.getLogger()

vpcs_opr = VpcOperator()
nets_opr = NetOperator()

class VpcDelete(WorkflowTask):

    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        v = vpcs_opr.store.get_vpc(self.param.name)
        v.set_obj_spec(self.param.spec)
        # TODO: Handle the error when all nets have not been deleted.
        while len(nets_opr.store.get_nets_in_vpc(v.name)):
            pass
        vpcs_opr.deallocate_vni(v)
        vpcs_opr.delete_vpc_dividers(v, v.n_dividers)
        v.delete_obj()
        vpcs_opr.store.delete_vpc(v.name)
        self.finalize()

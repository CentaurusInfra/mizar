import kopf
import logging
import asyncio
import luigi
from common.common import *
from common.constants import *
from common.wf_factory import *
from common.wf_param import *

LOCK: asyncio.Lock

@kopf.on.startup()
async def vpc_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    param = HandlerParam()
    run_task(wffactory().VpcOperatorStart(param=param))

# @kopf.on.delete(group, version, RESOURCES.vpcs)
# def vpc_opr_on_vpc_delete(body, **kwargs):
#     vpc_operator.on_vpc_delete(body, **kwargs)

@kopf.on.resume(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_init)
@kopf.on.update(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_init)
@kopf.on.create(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_init)
def vpc_opr_on_vpc_init(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().VpcCreate(param=param))

# @kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
# @kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
# @kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
# def vpc_opr_on_divider_provisioned(body, spec, **kwargs):
#     vpc_operator.on_divider_provisioned(body, spec, **kwargs)

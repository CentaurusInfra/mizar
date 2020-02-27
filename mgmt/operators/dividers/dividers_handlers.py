import kopf
import logging
import asyncio
from common.constants import *
from common.constants import group, version
from operators.dividers.dividers_operator import DividerOperator

LOCK: asyncio.Lock
divider_operator  = DividerOperator()

@kopf.on.startup()
async def divider_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    global divider_operator
    divider_operator.on_startup(logger, **kwargs)

@kopf.on.resume(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_allocated)
@kopf.on.update(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_allocated)
@kopf.on.create(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_allocated)
def divider_opr_on_vpc_allocated(body, spec, **kwargs):
    global divider_operator
    divider_operator.on_vpc_allocated(body, spec, **kwargs)

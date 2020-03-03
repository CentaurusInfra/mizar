import kopf
import logging
import asyncio
from common.constants import *
from common.constants import group, version
from operators.vpcs.vpcs_operator import VpcOperator

LOCK: asyncio.Lock
vpc_operator  = VpcOperator()

@kopf.on.startup()
async def vpc_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    global vpc_operator
    vpc_operator.on_startup(logger, **kwargs)

@kopf.on.delete(group, version, RESOURCES.vpcs)
def vpc_opr_on_vpc_delete(body, **kwargs):
    global vpc_operator
    vpc_operator.on_vpc_delete(body, **kwargs)

@kopf.on.resume(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_init)
@kopf.on.update(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_init)
@kopf.on.create(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_init)
def vpc_opr_on_vpc_init(body, spec, **kwargs):
    global vpc_operator
    vpc_operator.on_vpc_init(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
@kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
@kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
def vpc_opr_on_divider_provisioned(body, spec, **kwargs):
    global vpc_operator
    vpc_operator.on_divider_provisioned(body, spec, **kwargs)

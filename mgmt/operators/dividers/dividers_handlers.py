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

@kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
@kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
@kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
def divider_opr_on_divider_provisioned(body, spec, **kwargs):
    global divider_operator
    divider_operator.on_divider_provisioned(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_endpoint_ready)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_endpoint_ready)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_endpoint_ready)
def divider_opr_on_bouncer_endpoint_ready(body, spec, **kwargs):
    global divider_operator
    divider_operator.on_bouncer_endpoint_ready(body, spec, **kwargs)

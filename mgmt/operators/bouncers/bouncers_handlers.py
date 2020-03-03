import kopf
import logging
import asyncio
from common.constants import *
from common.constants import group, version
from operators.bouncers.bouncers_operator import BouncerOperator

LOCK: asyncio.Lock

logger = logging.getLogger()

bouncer_operator  = BouncerOperator()

@kopf.on.startup()
async def bouncer_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    global bouncer_operator
    bouncer_operator.on_startup(logger, **kwargs)

@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
def bouncer_opr_on_bouncer_provisioned(body, spec, **kwargs):
    global bouncer_operator
    bouncer_operator.on_bouncer_provisioned(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_placed)
@kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_placed)
@kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_placed)
def bouncer_opr_on_divider_placed(body, spec, **kwargs):
    global bouncer_operator
    bouncer_operator.on_divider_placed(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_allocated)
@kopf.on.update(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_allocated)
@kopf.on.create(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_allocated)
def bouncer_opr_on_endpoints_allocated(body, spec, **kwargs):
    global bouncer_operator
    bouncer_operator.on_endpoints_allocated(body, spec, **kwargs)
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

@kopf.on.resume(group, version, RESOURCES.nets, when=LAMBDAS.net_status_allocated)
@kopf.on.update(group, version, RESOURCES.nets, when=LAMBDAS.net_status_allocated)
@kopf.on.create(group, version, RESOURCES.nets, when=LAMBDAS.net_status_allocated)
def divider_opr_on_net_allocated(body, spec, **kwargs):
    global bouncer_operator
    bouncer_operator.on_net_allocated(body, spec, **kwargs)


@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
def divider_opr_on_bouncer_init(body, spec, **kwargs):
    global bouncer_operator
    bouncer_operator.on_bouncer_init(body, spec, **kwargs)
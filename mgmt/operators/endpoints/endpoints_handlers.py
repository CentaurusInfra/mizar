import kopf
import logging
import asyncio
from common.constants import *
from operators.endpoints.endpoints_operator import EndpointOperator

LOCK: asyncio.Lock
logger = logging.getLogger()
endpoints_operator = EndpointOperator()

@kopf.on.startup()
async def ep_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    global endpoints_operator
    endpoints_operator.on_startup(logger, **kwargs)

@kopf.on.delete(group, version, RESOURCES.endpoints)
def ep_opr_on_endpoint_delete(body, **kwargs):
    logger.info("ep_opr_on_endpoint_delete")
    global endpoints_operator
    endpoints_operator.on_endpoint_delete(body, **kwargs)

@kopf.on.resume(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_provisioned)
@kopf.on.update(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_provisioned)
@kopf.on.create(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_provisioned)
def ep_opr_on_endpoint_provisioned(body, spec, **kwargs):
    global endpoints_operator
    endpoints_operator.on_endpoint_provisioned(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_placed)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_placed)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_placed)
def ep_opr_on_bouncer_placed(body, spec, **kwargs):
    global endpoints_operator
    endpoints_operator.on_bouncer_placed(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
def ep_opr_on_bouncer_provisioned(body, spec, **kwargs):
    global endpoints_operator
    endpoints_operator.on_bouncer_provisioned(body, spec, **kwargs)
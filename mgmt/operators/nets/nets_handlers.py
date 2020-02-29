import kopf
import logging
import asyncio
from common.constants import *
from common.constants import group, version
from operators.nets.nets_operator import NetOperator

logger = logging.getLogger()

LOCK: asyncio.Lock

net_operator = NetOperator()

@kopf.on.startup()
async def net_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    global net_operator
    net_operator.on_startup(logger, **kwargs)

@kopf.on.delete(group, version, RESOURCES.nets)
def net_opr_on_net_delete(body, **kwargs):
    global net_operator
    net_operator.on_net_delete(body, **kwargs)

@kopf.on.resume(group, version, RESOURCES.nets, when=LAMBDAS.net_status_init)
@kopf.on.update(group, version, RESOURCES.nets, when=LAMBDAS.net_status_init)
@kopf.on.create(group, version, RESOURCES.nets, when=LAMBDAS.net_status_init)
def net_opr_on_net_init(body, spec, **kwargs):
    global net_operator
    net_operator.on_net_init(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
def net_opr_on_bouncer_provisioned(body, spec, **kwargs):
    global net_operator
    net_operator.on_bouncer_provisioned(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.endpoints, when=LAMBDAS.endpoint_status_init)
@kopf.on.update(group, version, RESOURCES.endpoints, when=LAMBDAS.endpoint_status_init)
@kopf.on.create(group, version, RESOURCES.endpoints, when=LAMBDAS.endpoint_status_init)
def net_opr_on_endpoint_init(body, spec, **kwargs):
    global net_operator
    net_operator.on_endpoint_init(body, spec, **kwargs)

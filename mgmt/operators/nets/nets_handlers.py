import kopf
import logging
import asyncio
from common.constants import *
from common.constants import group, version
from operators.nets.nets_operator import NetOperator

logger = logging.getLogger()

resource = 'nets'
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
def vpc_opr_on_net_init(body, spec, **kwargs):
    global net_operator
    net_operator.on_net_init(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.nets, when=LAMBDAS.net_status_ready)
@kopf.on.update(group, version, RESOURCES.nets, when=LAMBDAS.net_status_ready)
@kopf.on.create(group, version, RESOURCES.nets, when=LAMBDAS.net_status_ready)
def vpc_opr_on_net_ready(body, spec, **kwargs):
    global net_operator
    net_operator.on_net_ready(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_provisioned)
@kopf.on.update(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_provisioned)
@kopf.on.create(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_provisioned)
def vpc_opr_on_vpc_provisioned(body, spec, **kwargs):
    global net_operator
    net_operator.on_vpc_provisioned(body, spec, **kwargs)

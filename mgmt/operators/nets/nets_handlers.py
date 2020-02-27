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

@kopf.on.resume(group, version, RESOURCES.nets)
@kopf.on.update(group, version, RESOURCES.nets)
@kopf.on.create(group, version, RESOURCES.nets)
def net_opr_on_net_update_any(body, spec, **kwargs):
    global net_operator
    net_operator.on_net_update_any(body, spec, **kwargs)

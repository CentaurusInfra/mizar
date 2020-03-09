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
async def divider_opr_on_startup(logger, **kwargs):
	global LOCK
	LOCK = asyncio.Lock()
	param = HandlerParam()
	run_task(wffactory().DividerOperatorStart(param=param))

@kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
@kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
@kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
def divider_opr_on_divider_init(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().DividerCreate(param=param))

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

@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
def bouncer_opr_on_bouncer_init(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().BouncerCreate(param=param))


@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_provisioned)
def bouncer_opr_on_bouncer_provisioned(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().BouncerProvisioned(param=param))

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
async def net_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    param = HandlerParam()
    run_task(wffactory().NetOperatorStart(param=param))

# @kopf.on.delete(group, version, RESOURCES.vpcs)
# def vpc_opr_on_vpc_delete(body, **kwargs):
#     vpc_operator.on_vpc_delete(body, **kwargs)

@kopf.on.resume(group, version, RESOURCES.nets, when=LAMBDAS.net_status_init)
@kopf.on.update(group, version, RESOURCES.nets, when=LAMBDAS.net_status_init)
@kopf.on.create(group, version, RESOURCES.nets, when=LAMBDAS.net_status_init)
def net_opr_on_net_init(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().NetCreate(param=param))

@kopf.on.resume(group, version, RESOURCES.nets, when=LAMBDAS.net_status_provisioned)
@kopf.on.update(group, version, RESOURCES.nets, when=LAMBDAS.net_status_provisioned)
@kopf.on.create(group, version, RESOURCES.nets, when=LAMBDAS.net_status_provisioned)
def net_opr_on_net_provisioned(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	param.diff = kwargs['diff']
	run_task(wffactory().NetProvisioned(param=param))


@kopf.on.delete(group, version, RESOURCES.nets)
def  net_opr_on_net_delete(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().NetDelete(param=param))
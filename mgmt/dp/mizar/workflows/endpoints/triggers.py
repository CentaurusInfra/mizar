import kopf
import logging
import asyncio
from common.common import *
from common.constants import *
from common.wf_factory import *
from common.wf_param import *

logger = logging.getLogger()

@kopf.on.resume(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_init)
@kopf.on.update(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_init)
@kopf.on.create(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_init)
def endpoint_opr_on_endpoint_init(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().EndpointCreate(param=param))


@kopf.on.resume(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_provisioned)
@kopf.on.update(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_provisioned)
@kopf.on.create(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_provisioned)
def endpoint_opr_on_endpoint_provisioned(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().EndpointProvisioned(param=param))

@kopf.on.delete(group, version, RESOURCES.endpoints)
def endpoint_opr_on_endpoint_delete(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().EndpointDelete(param=param))

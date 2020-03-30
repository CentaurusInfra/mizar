import kopf
import logging
import luigi
from common.common import *
from common.constants import *
from common.wf_factory import *
from common.wf_param import *

@kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
@kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
@kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
def divider_opr_on_divider_init(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().DividerCreate(param=param))


@kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
@kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
@kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_provisioned)
def divider_opr_on_divider_provisioned(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().DividerProvisioned(param=param))

@kopf.on.delete(group, version, RESOURCES.dividers)
def  divider_opr_on_divider_delete(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().DividerDelete(param=param))
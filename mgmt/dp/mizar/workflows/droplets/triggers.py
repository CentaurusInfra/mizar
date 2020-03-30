import kopf
import logging
import asyncio
from common.common import *
from common.constants import *
from common.wf_factory import *
from common.wf_param import *

@kopf.on.resume(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_init)
@kopf.on.update(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_init)
@kopf.on.create(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_init)
def droplet_opr_on_droplet_init(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().DropletCreate(param=param))

@kopf.on.resume(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_provisioned)
@kopf.on.update(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_provisioned)
@kopf.on.create(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_provisioned)
def droplet_opr_on_droplet_provisioned(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().DropletProvisioned(param=param))

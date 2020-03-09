import kopf
import logging
import asyncio
from common.constants import *
from common.constants import group, version
from operators.droplets.droplets_operator import DropletOperator

LOCK: asyncio.Lock
droplet_operator  = DropletOperator()

@kopf.on.startup()
async def droplet_opr_on_startup(logger, **kwargs):
    global LOCK
    LOCK = asyncio.Lock()
    global droplet_operator
    droplet_operator.on_startup(logger, **kwargs)

@kopf.on.resume(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_init)
@kopf.on.update(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_init)
@kopf.on.create(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_init)
def droplet_opr_on_droplet_init(body, spec, **kwargs):
    global droplet_operator
    droplet_operator.on_droplet_init(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_provisioned)
@kopf.on.update(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_provisioned)
@kopf.on.create(group, version, RESOURCES.droplets, when=LAMBDAS.droplet_status_provisioned)
def droplet_opr_on_droplet_provisioned(body, spec, **kwargs):
    global droplet_operator
    droplet_operator.on_droplet_provisioned(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
@kopf.on.update(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
@kopf.on.create(group, version, RESOURCES.bouncers, when=LAMBDAS.bouncer_status_init)
def droplet_opr_on_bouncer_init(body, spec, **kwargs):
    global droplet_operator
    droplet_operator.on_bouncer_init(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
@kopf.on.update(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
@kopf.on.create(group, version, RESOURCES.dividers, when=LAMBDAS.divider_status_init)
def droplet_opr_on_divider_init(body, spec, **kwargs):
    global droplet_operator
    droplet_operator.on_divider_init(body, spec, **kwargs)

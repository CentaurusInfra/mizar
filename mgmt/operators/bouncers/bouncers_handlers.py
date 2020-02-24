import kopf
import logging

from common.constants import *
from operators.bouncers.bouncers_operator import BouncerOperator

logger = logging.getLogger()

resource = 'bouncers'
bouncer_operator  = BouncerOperator()

@kopf.on.create(group, version, resource)
def create_bouncer(body, spec, **kwargs):
    logger.info("create_bouncer")
    global bouncer_operator
    bouncer_operator.on_create(body, spec, **kwargs)

@kopf.on.update(group, version, resource)
def update_bouncer(body, spec, **kwargs):
    logger.info("update_bouncer")
    global bouncer_operator
    bouncer_operator.on_update(body, spec, **kwargs)

@kopf.on.resume(group, version, resource)
def resume_bouncer(body, spec, **kwargs):
    logger.info("resume_bouncer")
    global bouncer_operator
    bouncer_operator.on_resume(body, spec, **kwargs)

@kopf.on.delete(group, version, resource)
def delete_bouncer(body, **kwargs):
    logger.info("delete_bouncer")
    global bouncer_operator
    bouncer_operator.on_delete(body, **kwargs)

@kopf.on.resume(group, version, 'endpoints', when=lambda body, **_: body.get('spec', {}).get('status', '') == 'ready')
@kopf.on.update(group, version, 'endpoints', when=lambda body, **_: body.get('spec', {}).get('status', '') == 'ready')
@kopf.on.create(group, version, 'endpoints', when=lambda body, **_: body.get('spec', {}).get('status', '') == 'ready')
def when_ep_is_alloc(body, spec, **kwargs):
    logger.info("@@@ bouncer sees endpoint status: {}".format(spec['status']))
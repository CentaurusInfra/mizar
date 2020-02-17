import kopf
import logging

from common.constants import group, version
from dividers.dividers_operator import DividerOperator

logger = logging.getLogger()

resource = 'dividers'
divider_operator  = DividerOperator(arg1="arg1", hello="hello2222")

@kopf.on.create(group, version, resource)
def create_divider(body, spec, **kwargs):
    logger.info("create_divider")
    global divider_operator
    divider_operator.on_create(body, spec, **kwargs)

@kopf.on.update(group, version, resource)
def update_divider(body, spec, **kwargs):
    logger.info("update_divider")
    global divider_operator
    divider_operator.on_update(body, spec, **kwargs)

@kopf.on.resume(group, version, resource)
def resume_divider(spec, **kwargs):
    logger.info("resume_divider")
    global divider_operator
    divider_operator.on_resume(spec, **kwargs)

@kopf.on.delete(group, version, resource)
def delete_divider(body, **kwargs):
    logger.info("delete_divider")
    global divider_operator
    divider_operator.on_delete(body, **kwargs)
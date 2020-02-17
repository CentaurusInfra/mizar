import kopf
import logging

from common.constants import group, version
from vpcs.vpcs_operator import VpcOperator

logger = logging.getLogger()

resource = 'vpcs'
vpc_operator  = VpcOperator(arg1="arg1", hello="hello2222")

@kopf.on.create(group, version, resource)
def create_vpc(body, spec, **kwargs):
    logger.info("create_vpc")
    global vpc_operator
    vpc_operator.on_create(body, spec, **kwargs)

@kopf.on.update(group, version, resource)
def update_vpc(body, spec, **kwargs):
    logger.info("update_vpc")
    global vpc_operator
    vpc_operator.on_update(body, spec, **kwargs)

@kopf.on.resume(group, version, resource)
def resume_vpc(body, spec, **kwargs):
    logger.info("resume_vpc")
    global vpc_operator
    vpc_operator.on_resume(body, spec, **kwargs)

@kopf.on.delete(group, version, resource)
def delete_vpc(body, **kwargs):
    logger.info("delete_vpc")
    global vpc_operator
    vpc_operator.on_delete(body, **kwargs)
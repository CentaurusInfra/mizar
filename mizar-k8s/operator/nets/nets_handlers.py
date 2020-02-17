import kopf
import logging

from common.constants import group, version
from nets.nets_operator import NetOperator

logger = logging.getLogger()

resource = 'nets'
net_operator = NetOperator(arg1="arg1", hello="hello")

@kopf.on.create(group, version, resource)
def create_net(body, spec, **kwargs):
    logger.info("create_net")
    global net_operator
    net_operator.on_create(body, spec, **kwargs)

@kopf.on.update(group, version, resource)
def update_net(body, spec, **kwargs):
    logger.info("update_net")
    global net_operator
    net_operator.on_update(body, spec, **kwargs)

@kopf.on.resume(group, version, resource)
def resume_net(body, spec, **kwargs):
    logger.info("resume_net")
    global net_operator
    net_operator.on_resume(body, spec, **kwargs)

@kopf.on.delete(group, version, resource)
def delete_net(body, **kwargs):
    logger.info("delete_net")
    global net_operator
    net_operator.on_delete(body, **kwargs)

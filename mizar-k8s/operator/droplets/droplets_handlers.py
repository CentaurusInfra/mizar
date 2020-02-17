import kopf
import logging

from common.constants import group, version
from opr.droplets_operator import DropletOperator

logger = logging.getLogger()

droplet_operator  = DropletOperator(arg1="arg1", hello="hello2222")

@kopf.on.create(group, version, 'droplets')
def create_droplet(body, spec, **kwargs):
    logger.info("create_droplet")
    global droplet_operator
    droplet_operator.on_create(body, spec, **kwargs)

@kopf.on.update(group, version, 'droplets')
def update_droplet(body, spec, **kwargs):
    logger.info("update_droplet")
    global droplet_operator
    droplet_operator.on_update(body, spec, **kwargs)

@kopf.on.resume(group, version, 'droplets')
def resume_droplet(spec, **kwargs):
    logger.info("resume_droplet")
    global droplet_operator
    droplet_operator.on_resume(spec, **kwargs)

@kopf.on.delete(group, version, 'droplets')
def delete_droplet(body, **kwargs):
    logger.info("delete_droplet")
    global droplet_operator
    droplet_operator.on_delete(body, **kwargs)
#!/usr/bin/python3

import kopf
import logging

from opr.droplets_operator import DropletOperator
from opr.endpoints_operator import EndpointOperator
from opr.vpcs_operator import VpcOperator

logger = logging.getLogger()
group = 'mizar.com'
version = 'v1'

droplet_operator  = DropletOperator(arg1="arg1", hello="hello")
endpoint_operators = EndpointOperator(arg1="arg1", hello="hello")

@kopf.on.create(group, version, 'endpoints')
def create_endpoint(body, spec, **kwargs):
    logger.info("create_endpoint")
    global endpoints_operator
    endpoint_operators.on_create(body, spec, **kwargs)

@kopf.on.update(group, version, 'endpoints')
def update_endpoint(body, spec, **kwargs):
    logger.info("update_endpoint")
    global endpoints_operator
    endpoint_operators.on_update(body, spec, **kwargs)

@kopf.on.resume(group, version, 'endpoints')
def resume_endpoints(spec, **kwargs):
    logger.info("resume_endpoints")
    global endpoints_operator
    endpoint_operators.on_resume(spec, **kwargs)

@kopf.on.delete(group, version, 'endpoints')
def delete_endpoint(body, **kwargs):
    logger.info("delete_endpoint")
    global endpoints_operator
    endpoint_operators.on_delete(body, **kwargs)

############################################

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
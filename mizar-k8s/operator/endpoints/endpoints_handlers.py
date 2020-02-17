import kopf
import logging

from common.constants import group, version
from endpoints.endpoints_operator import EndpointOperator

logger = logging.getLogger()

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

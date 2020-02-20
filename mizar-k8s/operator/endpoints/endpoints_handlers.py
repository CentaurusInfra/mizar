import kopf
import logging

from common.constants import group, version
from endpoints.endpoints_operator import EndpointOperator

logger = logging.getLogger()

resource = 'endpoints'
endpoint_operators = EndpointOperator()

@kopf.on.create(group, version, resource)
def create_endpoint(body, spec, **kwargs):
    logger.info("create_endpoint")
    global endpoints_operator
    endpoint_operators.on_create(body, spec, **kwargs)

@kopf.on.update(group, version, resource)
def update_endpoint(body, spec, **kwargs):
    logger.info("update_endpoint")
    global endpoints_operator
    endpoint_operators.on_update(body, spec, **kwargs)

@kopf.on.resume(group, version, resource)
def resume_endpoints(body, spec, **kwargs):
    logger.info("resume_endpoints")
    global endpoints_operator
    endpoint_operators.on_resume(body, spec, **kwargs)

@kopf.on.delete(group, version, resource)
def delete_endpoint(body, **kwargs):
    logger.info("delete_endpoint")
    global endpoints_operator
    endpoint_operators.on_delete(body, **kwargs)

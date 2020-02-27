import kopf
import logging

from common.constants import *
from operators.endpoints.endpoints_operator import EndpointOperator

logger = logging.getLogger()

endpoint_operators = EndpointOperator()

@kopf.on.delete(group, version, RESOURCES.endpoints)
def ep_opr_on_endpoint_delete(body, **kwargs):
    logger.info("ep_opr_on_endpoint_delete")
    global endpoints_operator
    endpoint_operators.on_endpoint_delete(body, **kwargs)

@kopf.on.resume(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_init)
@kopf.on.update(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_init)
@kopf.on.create(group, version, RESOURCES.endpoints, when=LAMBDAS.ep_status_init)
def ep_opr_on_endpoint_init(body, spec, **kwargs):
    global endpoints_operator
    endpoint_operators.on_endpoint_init(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_provisioned)
@kopf.on.update(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_provisioned)
@kopf.on.create(group, version, RESOURCES.vpcs, when=LAMBDAS.vpc_status_provisioned)
def ep_opr_on_vpc_provisioned(body, spec, **kwargs):
    global endpoints_operator
    endpoint_operators.on_vpc_provisioned(body, spec, **kwargs)

@kopf.on.resume(group, version, RESOURCES.nets, when=LAMBDAS.net_status_provisioned)
@kopf.on.update(group, version, RESOURCES.nets, when=LAMBDAS.net_status_provisioned)
@kopf.on.create(group, version, RESOURCES.nets, when=LAMBDAS.net_status_provisioned)
def ep_opr_on_net_provisioned(body, spec, **kwargs):
    global endpoints_operator
    endpoint_operators.on_net_provisioned(body, spec, **kwargs)
import kopf
import logging
import luigi
from common.common import *
from common.constants import *
from common.wf_factory import *
from common.wf_param import *

logger = logging.getLogger()
mizar_service_annotation_key = "service.beta.kubernetes.io/mizar-scaled-endpoint-type"
mizar_service_annotation_val = "scaled-endpoint"
annotations_filter = {mizar_service_annotation_key: mizar_service_annotation_val}

@kopf.on.resume('', 'v1', 'services', annotations=annotations_filter)
@kopf.on.update('', 'v1', 'services', annotations=annotations_filter)
@kopf.on.create('', 'v1', 'services', annotations=annotations_filter)
async def services_opr_on_services(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().k8sServiceCreate(param=param))


@kopf.on.resume('', 'v1', 'endpoints')
@kopf.on.update('', 'v1', 'endpoints')
@kopf.on.create('', 'v1', 'endpoints')
async def services_opr_on_endpoints(body, spec, **kwargs):
	param = HandlerParam()
	param.name = kwargs['name']
	param.body = body
	param.spec = spec
	run_task(wffactory().k8sEndpointsUpdate(param=param))
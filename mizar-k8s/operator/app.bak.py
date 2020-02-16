#!/usr/bin/python3

import kopf
import kubernetes
import yaml
import json
import logging

logger=logging.getLogger()

counter = 0

class endpoint:
    def __init__(self, name, body, core_api, obj_api):
        self.core_api = core_api
        self.obj_api = obj_api
        self.mac = ""
        self.ip = ""
        self.prefix = ""
        self.gw = ""
        self.interface_index = "0"
        self.status = "init"
        self.name = name
        self.body = body
        self.obj = None

    def get_obj_spec(self):
        self.obj = {
                "type": "simple",
                "status": self.status,
                "ip": self.ip,
                "mac": self.mac,
                "gw": self.gw
        }

        return self.obj

    def prepare(self):
        self.allocate_ip()
        self.get_gw()
        self.allocate_mac()
        self.status='ready'

    def allocate_ip(self):
        self.ip = "10.0.0.2"

    def get_gw(self):
        self.gw = "10.0.0.1"

    def allocate_mac(self):
        self.mac = "1:2:3:4"

    def update_endpoint(self):
        # update the resource
        self.body['spec'] = self.get_obj_spec()
        self.obj_api.patch_namespaced_custom_object(
            group="mizar.com",
            version="v1",
            namespace="default",
            plural="endpoints",
            name=self.name,
            body=self.body
        )

@kopf.on.create('mizar.com', 'v1', 'endpoints')
def create_fn(body, spec, **kwargs):
    # Get info from Database object
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']
    type = spec['type']
    status = spec['status']
    global counter

    logger.info(body)
    # Make sure type is provided
    if not type:
        raise kopf.HandlerFatalError(f"Type must be set. Got {type}.")

    # Object used to communicate with the API Server
    core_api = kubernetes.client.CoreV1Api()
    obj_api = kubernetes.client.CustomObjectsApi()

    ep = endpoint(name, body, core_api, obj_api)
    ep.prepare()
    ep.update_endpoint()
    logger.info("$$$$ modified {}".format(ep.get_obj_spec()))
    counter += 1
    print(f"Endpoints Operator Dude!")

    # Update status
    msg = f"Operator created {name}, {counter}"
    return {'message': msg}

@kopf.on.delete('mizar.com', 'v1', 'endpoints')
def delete(body, **kwargs):
    # Get info from Database object
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']

    msg = f"Operator deleted {name}"
    return {'message': msg}

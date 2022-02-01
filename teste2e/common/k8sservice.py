from teste2e.common.helper import *
from time import sleep
from mizar.common.constants import *

SCRIPTS_DIR = '/var/mizar/test/scripts'


class k8sService:

    def __init__(self, api, name, ip):
        self.api = api
        self.name = name
        self.ip = ip
        self.endpoints = {}

    @property
    def eptype(self):
        return "scaled"

    @property
    def backends(self):
        return set(self.endpoints.keys())

    def add_endpoint(self, name, vpc_name=OBJ_DEFAULTS.default_ep_vpc, subnet_name=OBJ_DEFAULTS.default_ep_net):
        ep = self.api.create_pod(
            name, vpc_name, subnet_name, scaledep=self.name)
        self.endpoints[ep.name] = ep

from teste2e.common.helper import *
from time import sleep

SCRIPTS_DIR = '/var/mizar/test/scripts'

class k8sService:

    def __init__(self, api, name, ip):
        self.api = api
        self.name = name
        self.ip = ip
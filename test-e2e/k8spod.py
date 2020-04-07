from common import *

class k8sPod:

    def __init__(self, api, name, ip):
        self.api = api
        self.name = name
        self.ip = ip

    def ping(self, ip):
        cmd = 'ping -c 3 {}'.format(ip)
        err = self.api.pod_exec(self.name, cmd)
        if err['status'] != "Success":
            return False
        return True


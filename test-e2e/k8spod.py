from common import *
from time import sleep

SCRIPTS_DIR = '/var/mizar/test/scripts'

class k8sPod:

    def __init__(self, api, name, ip):
        self.api = api
        self.name = name
        self.ip = ip

    def do_ping(self, server, count=1, wait=5):
        ip = server.ip
        cmd = 'ping -w {} -c {} {}'.format(wait, count, ip)
        err = self.api.pod_exec(self.name, cmd)
        logger.info("do_ping output {}, got: {}".format(self.name, err))
        return err['status'] == "Success"

    def do_curl_hostname(self, server):
        ip = server.ip
        cmd = f'''/bin/bash {SCRIPTS_DIR}/curl_client_hostname.sh {ip}'''
        out = self.api.pod_exec_stdout(self.name, cmd)
        logger.info("do_curl_client {}, got: {}".format(self.name, out))
        return out == server.name

    def do_tcp_hostname(self, server):
        ip = server.ip
        cmd = f'''/bin/bash {SCRIPTS_DIR}/nc_client_hostname.sh {ip}'''
        out = self.api.pod_exec_stdout(self.name, cmd)
        logger.info("do_tcp_client {}, got: {}".format(self.name, out))
        return out == server.name

    def do_udp_hostname(self, server):
        ip = server.ip
        cmd = f'''/bin/bash {SCRIPTS_DIR}/nc_client_hostname.sh {ip} udp'''
        out = self.api.pod_exec_stdout(self.name, cmd)
        logger.info("do_udp_client {}, got: {}".format(self.name, out))
        return out == server.name

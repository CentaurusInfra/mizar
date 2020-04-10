from common import *
from time import sleep

class k8sPod:

    def __init__(self, api, name, ip):
        self.api = api
        self.name = name
        self.ip = ip

    def do_ping(self, ip, count=1, wait=5):
        cmd = 'ping -w {} -c {} {}'.format(wait, count, ip)
        err = self.api.pod_exec(self.name, cmd)
        logging.debug("[DEBUG] do_ping output: {}".format(err))
        if err['status'] != "Success":
            return False
        return True

    def do_curl(self, args):
        cmd = 'curl {}'.format(args)
        err = self.api.pod_exec(self.name, cmd)
        logging.debug("[DEBUG] do_curl output: {}".format(err))
        if err['status'] != "Success":
            return False
        return True

    def do_tcp_client(self, ip, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        dd_cmd = 'dd if=/dev/random  bs={} count={} | tee /tmp/nc_tcp.sent'.format(bs, count)
        cmd = '/bin/sh -c {} | nc {} 9001 {} -w1'.format(dd_cmd, ip, delay)
        err = self.api.pod_exec(self.name, cmd)
        logging.debug("[DEBUG] do_tcp_client output: {}".format(err))
        if err['status'] != "Success":
            return False
        return True

    def do_udp_client(self, ip, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        dd_cmd = 'dd if=/dev/random  bs={} count={} | tee /tmp/nc_udp.sent'.format(bs, count)
        cmd = '/bin/sh -c {} | nc -u {} 5001 {} -w1'.format(dd_cmd, ip, delay)
        err = self.api.pod_exec(self.name, cmd)
        logging.debug("[DEBUG] do_udp_client output: {}".format(err))
        if err['status'] != "Success":
            return False
        return True

    def do_tcp_diff(self, name):
        sent_cmd = '/bin/sh -c cat /tmp/nc_tcp.sent'
        client_output = self.api.pod_exec_stdout(self.name, sent_cmd)

        recv_cmd = '/bin/sh -c cat /tmp/nc_tcp.recv'
        server_output = self.api.pod_exec_stdout(name, recv_cmd)

        if client_output == server_output:
            return True
        return False

    def do_udp_diff(self, name):
        sent_cmd = '/bin/sh -c cat /tmp/nc_udp.sent'
        client_output = self.api.pod_exec_stdout(self.name, sent_cmd)

        recv_cmd = '/bin/sh -c cat /tmp/nc_udp.recv'
        server_output = self.api.pod_exec_stdout(name, recv_cmd)

        if client_output == server_output:
            return True
        return False

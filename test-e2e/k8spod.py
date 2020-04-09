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
        logging.debug("PING OUTPUT {}:".format(err))
        if err['status'] != "Success":
            return False
        return True

    def do_curl(self, args):
        cmd = 'curl {}'.format(args)
        err = self.api.pod_exec(self.name, cmd)
        logging.debug("CURL OUTPUT {}:".format(err))
        if err['status'] != "Success":
            return False
        return True

    # def do_httpd(self):
    #     cmd = 'pushd /tmp; python3 -m http.server > /tmp/httpd.log 2>&1'
    #     err = self.api.pod_exec(self.name, cmd)
    #     sleep(1)
    #     if err['status'] != "Success":
    #         return False
    #     return True

    # def do_tcp_serve(self):
    #     cmd = "nc -l -p 9001 > /tmp/tcp_recv_file"
    #     err = self.api.pod_exec(self.name, cmd)
    #     if err['status'] != "Success":
    #         return False
    #     return True

    # def do_udp_serve(self):
    #     cmd = "nc -u -l -p 5001 > /tmp/udp_recv_file"
    #     err = self.api.pod_exec(self.name, cmd)
    #     if err['status'] != "Success":
    #         return False
    #     return True

    def do_tcp_client(self, ip, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        #dd_cmd = 'dd if=/dev/urandom  bs={} count={} | tee /tmp/tcp_sent_file'.format(bs, count)
        #cmd = '/bin/sh -c ({} | nc {} 9001 {} -w1)'.format(dd_cmd, ip, delay)
        cmd = 'nc -z -v -n {} 9001'.format(self.ip)
        err = self.api.pod_exec(self.name, cmd)
        logging.debug("NC TCP OUTPUT: {}".format(err))
        if err['status'] != "Success":
            return False
        return True

    def do_udp_client(self, ip, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        #dd_cmd = 'dd if=/dev/urandom  bs={} count={} | tee /tmp/udp_sent_file'.format(bs, count)
        #cmd = '/bin/sh -c ({} | nc -u {} 5001 {} -w1)'.format(dd_cmd, ip, delay)
        cmd = 'nc -u -z -v -n {} 5001'.format(self.ip)
        err = self.api.pod_exec(self.name, cmd)
        logging.debug("NC UDP OUTPUT: {}".format(err))
        if err['status'] != "Success":
            return False
        return True

    # def do_diff_tcp(self, client_ep, server_ep):
    #     cmd = 'diff /tmp/tcp_recv_file /tmp/tcp_sent_file'
    #     err = self.api.pod_exec(self.name, cmd)
    #     print("DIFF TCP ERROR: {}".format(err))
    #     if err['status'] != "Success":
    #         return False
    #     return True
    #
    # def do_diff_tcp(self, client_ep, server_ep):
    #     cmd = 'diff /tmp/udp_recv_file /tmp/udp_sent_file'
    #     err = self.api.pod_exec(self.name, cmd)
    #     print("DIFF UDP ERROR: {}".format(err))
    #     if err['status'] != "Success":
    #         return False
    #     return True

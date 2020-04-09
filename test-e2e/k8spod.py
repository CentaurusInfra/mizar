from common import *
from time import sleep

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

    def http(self, client_name):
        httpd_cmd = '/bin/sh -c python3 -m http.server'
        self.api.pod_exec2(self.name, httpd_cmd)
        sleep(1)
        #print("OUTPUT {}".format(err))

        curl_cmd = 'curl http://{}:8000 -Ss -m 1'.format(self.ip)
        self.api.pod_exec2(client_name, curl_cmd)
#        err = self.api.pod_exec(client_name, curl_cmd)
#        print("OUTPUT CURL {}".format(err))
#        if err['status'] != "Success":
#            return False
        return True

    def tcp(self, client_name):
        output_dir = '/tmp'
        tcp_recv_file = '{}/{}_{}_tcp_recv'.format(output_dir, self.name, self.ip)
        tcp_sent_file = '{}/{}_{}_tcp_sent'.format(output_dir, self.name, self.ip)

        cmd_nc = '/bin/sh -c (nc -l -p 9001 > {})'.format(tcp_recv_file)
        err = self.api.pod_exec(self.name, cmd_nc)
        print("OUTPUT NC {}".format(err))
        if err['status'] != "Success":
            return False

        self.tcp_client(client_name, self.ip, tcp_sent_file)
        
        cmd_diff = 'diff {} {}'.format(tcp_recv_file, tcp_sent_file)
        err = self.api.pod_exec(client_name, cmd_diff)
        if err['status'] != "Success":
            return False
        return True

    def tcp_client(self, name, ip, tcp_sent_file, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        dd_cmd = 'dd if=/dev/urandom  bs={bs} count={count} | tee {}'.format(tcp_sent_file)
        cmd = '/bin/sh ({} | nc {} 9001 {} -w1)'.format(dd_cmd, ip, delay)
        err = self.api.pod_exec(name, cmd)
        print("OUTPUT CLIENT {}".format(err))
        if err['status'] != "Success":
            return False

    def udp(self):
        output_dir = '/tmp'
        udp_recv_file = '{}/{}_{}_udp_recv'.format(output_dir, self.name, self.ip)
        udp_sent_file = '{}/{}_{}_udp_sent'.format(output_dir, self.name, self.ip)

        cmd_nc = '/bin/sh -c (nc -u -l -p 5001 > {})'.format(udp_recv_file)
        err = self.api.pod_exec(self.name, cmd_nc)
        print("OUTPUT NC {}".format(err))
        if err['status'] != "Success":
            return False

        self.udp_client(client_name, self.ip, udp_sent_file)

        cmd_diff = 'diff {} {}'.format(tcp_recv_file, tcp_sent_file)
        err = self.api.pod_exec(client_name, cmd_diff)
        if err['status'] != "Success":
            return False
        return True

    def udp_client(self, name, ip, udp_sent_file, bs=100, count=1, interval=0, detach=False):
        delay = ''
        if interval > 0:
            delay = '-i{}'.format(interval)
        dd_cmd = 'dd if=/dev/urandom  bs={bs} count={count} | tee {}'.format(udp_sent_file)
        cmd = '/bin/sh ({} | nc -u {} 5001 {} -w1)'.format(dd_cmd, ip, delay)
        err = self.api.pod_exec(name, cmd)
        print("OUTPUT CLIENT {}".format(err))
        if err['status'] != "Success":
            return False

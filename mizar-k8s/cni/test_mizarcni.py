#!/usr/bin/python3

import os
import subprocess
import sys
from subprocess import Popen, PIPE, STDOUT

def main():

	os.environ["CNI_COMMAND"] ='ADD'
	os.environ["CNI_CONTAINERID"] = '320f60a0fce865a9e05a6b8e65dcb0a691d699adafe6dbf4d978b5a718ec822a'
	os.environ["CNI_NETNS"] = '/var/run/netns/cni-825fc751-3ab9-45f2-420d-2159647a0500'
	os.environ["CNI_IFNAME"] = 'eth0'
	os.environ["CNI_PATH"] = '/opt/cni/bin'
	os.environ["CNI_ARGS"] = 'IgnoreUnknown=1;K8S_POD_NAMESPACE=default;K8S_POD_NAME=hello-world2-7556f76cd-8drvm;K8S_POD_INFRA_CONTAINER_ID=320f60a0fce865a9e05a6b8e65dcb0a691d699adafe6dbf4d978b5a718ec822a'

	stdin = '{"cniVersion":"0.2.0","k8sconfig":"/tmp/config","name":"mizarcni","type":"mizarcni.py"}'

	p = Popen(['./mizarcni.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
	(stdout_data, stderr_data) = p.communicate(input=stdin.encode('utf8'))

	print(stdout_data)
	print(stderr_data)


main()
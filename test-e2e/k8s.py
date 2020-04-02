from common import *
from cli.mizarapi import *
from kubernetes import client, config
from kubernetes.stream import stream


class k8sCluster:
    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super(k8sCluster, cls).__new__(cls)
            cls._init(cls, **kwargs)
        return cls._instance

    def _init(self):
        logger.info("Check or start existing cluster")
        if not self.is_running(self):
            self.start_cluster(self)
        else:
            logger.info("Test cluster is already running")

    def start_cluster(self):
        logger.info("Start test cluster")
        run_cmd("./kind-setup.sh")

    def is_running(self):
        ret, val = run_cmd("kind get clusters")
        return val.strip() == TEST_CLUSTER

    def delete_cluster(self):
        logger.info("Delete test cluster")
        run_cmd("kind delete cluster")


class k8sApi:

    def __init__(self):
        self.api = MizarApi()
        config.load_kube_config()
#		config.load_incluster_config()
        self.api_instance = client.CoreV1Api()

    def create_vpc(self, name, ip, prefix, dividers=1, vni=None):
        self.api.create_vpc(name, ip, prefix, dividers, vni)

    def create_net(self, name, ip, prefix, vpc, bouncers=1, vni=None):
        self.api.create_net(name, ip, prefix, vpc, bouncers, vni)

    def delete_vpc(self, name):
        self.api.delete_vpc(name)

    def delete_net(self, name):
        self.api.delete_net(name)

    def create_pod(self, name):
        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                    'name': name
            },
            'spec': {
                'containers': [{
                    'image': 'nginx:1.7.9',
                    'name': 'box1'
                }]
            }
        }

        resp = self.api_instance.create_namespaced_pod(
            body=pod_manifest, namespace='default')

        status = None
        while status != 'Running':
            resp = self.api_instance.read_namespaced_pod(
                name=name, namespace='default')
            status = resp.status.phase
        print("Done")
        print(status)

    def pod_exec(self, name):
        exec_command = [
            '/bin/bash',
            'tail -f /dev/null']
        resp = stream(self.api_instance.connect_get_namespaced_pod_exec,
                      name,
                      'default',
                      command=exec_command,
                      stderr=True, stdin=False,
                      stdout=True, tty=False)
        print("Response: " + resp)

#	def list_ip(self):
#		print("Listing pods with their IPs:")
#		ret = self.api_instance.list_pod_for_all_namespaces(watch=False)
#		for i in ret.items:
#			print("%s\t%s\t%s" %
#					(i.status.pod_ip, i.metadata.namespace, i.metadata.name))

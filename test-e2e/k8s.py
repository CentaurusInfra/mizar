import yaml
from common import *
from cli.mizarapi import *
from kubernetes import client, config
from kubernetes.stream import stream
from k8spod import *
from kubernetes.stream.ws_client import ERROR_CHANNEL

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
        run_cmd("./kind-setup.sh dev 2")

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
        self.k8sapi = client.CoreV1Api()

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
                    'image': 'localhost:5000/testpod:latest',
                    'name': 'box1'
                }]
            }
        }

        resp = self.k8sapi.create_namespaced_pod(
            body=pod_manifest, namespace='default')

        status = resp.status.phase
        while status != 'Running':
            resp = self.k8sapi.read_namespaced_pod(
                name=name, namespace='default')
            status = resp.status.phase

        pod = k8sPod(self, name, resp.status.pod_ip)
        logger.info("Pod {} IP {}".format(pod.name, pod.ip))
        return pod

    def delete_pod(self, name):
        self.k8sapi.delete_namespaced_pod(name=name, namespace='default')

        deleted = False
        while deleted:
            try:
                self.k8sapi.read_namespaced_pod(name=name, namespace='default')
            except:
                deleted = True
        logger.info("Deleted {}".format(name))

    def pod_exec(self, name, cmd):
        exec_command = cmd.split()
        resp = stream(self.k8sapi.connect_get_namespaced_pod_exec,
                      name,
                      'default',
                      command=exec_command,
                      stderr=True, stdin=False,
                      stdout=True, tty=False,
                      _preload_content=False)
        while resp.is_open():
            resp.update(timeout=1)
            err = resp.read_channel(ERROR_CHANNEL)
            if err:
                return yaml.load(err)

    def pod_exec_stdout(self, name, cmd):
        exec_command = cmd.split()
        resp = stream(self.k8sapi.connect_get_namespaced_pod_exec,
                      name,
                      'default',
                      command=exec_command,
                      stderr=True, stdin=False,
                      stdout=True, tty=False)
        return resp

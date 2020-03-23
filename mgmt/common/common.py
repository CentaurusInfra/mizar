import subprocess
import ctypes
import logging
import luigi
from kubernetes import watch, client
from ctypes.util import find_library
from pathlib import Path
_libc = ctypes.CDLL(find_library('c'), use_errno=True)

logger = logging.getLogger()

def run_cmd(cmd):
	result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	text = result.stdout.read().decode()
	returncode = result.returncode
	return (returncode, text)

def get_iface_index(name, iproute):
	return iproute.link_lookup(ifname=name)[0]

def get_iface_mac(idx, iproute):
	for (attr, val) in iproute.get_links(int(idx))[0]['attrs']:
		if attr == 'IFLA_ADDRESS':
			return val
	return None

def _nsfd(pid, ns_type):
    return Path('/proc') / str(pid) / 'ns' / ns_type

def host_nsenter(pid=1):
	_host_nsenter('mnt', pid)
	_host_nsenter('ipc', pid)
	_host_nsenter('net', pid)
	_host_nsenter('pid', pid)
	#_host_nsenter('user', pid)
	_host_nsenter('uts', pid)

def _host_nsenter(ns_type, pid=1):
	pid = pid

	target_fd = _nsfd(pid, ns_type).open()
	target_fileno = target_fd.fileno()

	if _libc.setns(target_fileno, 0) == -1:
		e = ctypes.get_errno()
		raise Exception('namespace switch {} {} error {}'.format(pid, ns_type, e))
		target_fd.close()


def kube_create_obj(obj):
	try:
		body = obj.obj_api.get_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural=obj.get_plural(),
			name=obj.get_name())
		spec = body['spec']
		obj.set_obj_spec(spec)
	except:
		body = {
			"apiVersion": "mizar.com/v1",
			"kind": obj.get_kind(),
			"metadata": {
				"name": obj.get_name()
			},
			"spec": obj.get_obj_spec()
		}

		obj.obj_api.create_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural=obj.get_plural(),
			body=body,
		)
		logger.debug("Created {} {}".format(obj.get_kind(), obj.get_name()))
	obj.store_update_obj()


def kube_update_obj(obj):
	get_body = True
	while get_body:
		body = obj.obj_api.get_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural=obj.get_plural(),
			name=obj.get_name())

		body['spec'] = obj.get_obj_spec()
		try:
			obj.obj_api.patch_namespaced_custom_object(
				group="mizar.com",
				version="v1",
				namespace="default",
				plural=obj.get_plural(),
				name=obj.name,
				body=body)
			obj.store_update_obj()
			get_body = False
		except:
			logger.debug("Retry updating {} {}".format(obj.get_kind(), obj.get_name()))
			get_body = True

def kube_delete_obj(obj):
	try:
		obj.obj_api.delete_namespaced_custom_object(
			group="mizar.com",
			version="v1",
			namespace="default",
			plural=obj.get_plural(),
			name=obj.name,
			body=client.V1DeleteOptions(),
			propagation_policy="Orphan")
	except:
		logger.debug("Failed to delete {} {}".format(obj.get_kind(), obj.get_name()))

def kube_watch_obj(obj, watch_callback):
	watcher = watch.Watch()
	stream = watcher.stream(obj.obj_api.list_namespaced_custom_object,
				group="mizar.com",
				version="v1",
				namespace="default",
				plural=obj.get_plural(),
				field_selector = "metadata.name={}".format(obj.get_name()),
				watch = True
			)

	for event in stream:
		name = event['object']['metadata']['name']
		if name == obj.name:
			spec = event['object']['spec']
			obj.set_obj_spec(spec)
			obj.store_update_obj()
		if watch_callback(event, obj):
			watcher.stop()
			return

def kube_list_obj(obj_api, plurals, list_callback):
	response = obj_api.list_namespaced_custom_object(
					group = "mizar.com",
					version = "v1",
					namespace = "default",
					plural = plurals,
					watch=False)
	items = response['items']
	for v in items:
		name = v['metadata']['name']
		spec = v['spec']
		list_callback(name, spec, plurals)

def get_spec_val(key, spec, default=""):
	return default if key not in spec else spec[key]

def run_workflow(wf):
    luigi.build(wf, workers=1, local_scheduler=True, log_level='INFO')

def run_task(task):
	sch = luigi.scheduler.Scheduler()

	# no_install_shutdown_handler makes it thread safe
	w = luigi.worker.Worker(scheduler=sch, no_install_shutdown_handler=True)
	w.add(task)
	w.run()
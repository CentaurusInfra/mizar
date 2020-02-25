import subprocess
import ctypes
from ctypes.util import find_library
from pathlib import Path
_libc = ctypes.CDLL(find_library('c'), use_errno=True)

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
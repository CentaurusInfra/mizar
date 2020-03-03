import sys
import logging
import rpyc
import logging
from common.cniparams import CniParams

logging.basicConfig(level=logging.INFO, filename='/tmp/cni.log')
sys.stderr = open('/tmp/cni.stderr', 'a')
logger = logging.getLogger()

def add():
	val, status = conn.root.add(params)
	logger.info("server's add is {} {}".format(val, status))
	print(val)
	exit(status)

def delete():
	val, status = conn.root.delete(params)
	logger.info("server's delete is {}".format(val))
	print(val)
	exit(status)


def get():
	val, status = conn.root.get(params)
	logger.info("server's get is {}".format(val))
	print(val)
	exit(status)

def version():
	val, status = conn.root.version(params)
	logger.info("server's version is {}".format(val))
	print(val)
	exit(status)

def cni():
	val = "Unsuported cni command!"
	switcher = {
		'ADD': add,
		'DEL': delete,
		'GET': get,
		'VERSION': version
	}

	func = switcher.get(params.command, lambda: "Unsuported cni command")
	if func:
		func()
	print(val)
	exit(1)

logger.info("CNI starting")
params = CniParams(''.join(sys.stdin.readlines()))
conn = rpyc.connect("localhost", 18861, config={"allow_all_attrs": True})
cni()



#!/usr/bin/python3
import subprocess
import logging
import time
import asyncio
import os.path
import time
from common.wf_param import *
from dp.mizar.workflows.vpcs.triggers import *
from dp.mizar.workflows.nets.triggers import *
from dp.mizar.workflows.dividers.triggers import *
from dp.mizar.workflows.bouncers.triggers import *
from dp.mizar.workflows.droplets.triggers import *
from dp.mizar.workflows.endpoints.triggers import *
from dp.mizar.workflows.builtins.services.triggers import *

logger = logging.getLogger()
LOCK: asyncio.Lock

@kopf.on.startup()
async def on_startup(logger, **kwargs):
	start_time = time.time()
	global LOCK
	LOCK = asyncio.Lock()
	param = HandlerParam()

	sched = 'luigid --background --port 8082 --pidfile /var/run/luigi/luigi.pid --logdir /var/log/luigi --state-path /var/lib/luigi/luigi.state'
	subprocess.call(sched, shell=True)
	while not os.path.exists("/var/run/luigi/luigi.pid"):
		pass
	with open('/var/run/luigi/luigi.pid', 'r') as f:
		pid = f.read()
	# Wait for daemon to run
	while not os.path.exists("/proc/{}".format(pid)):
		pass
	logger.info("Running luigid central scheduler pid={}!".format(pid))

	start_time = time.time()

	run_task(wffactory().DropletOperatorStart(param=param))
	run_task(wffactory().DividerOperatorStart(param=param))

	run_task(wffactory().VpcOperatorStart(param=param))

	run_task(wffactory().BouncerOperatorStart(param=param))

	run_task(wffactory().NetOperatorStart(param=param))
	run_task(wffactory().EndpointOperatorStart(param=param))

	logger.info("Bootstrap time:  %s seconds ---" % (time.time() - start_time))
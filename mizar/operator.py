#!/usr/bin/python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import subprocess
import logging
import time
import asyncio
import os.path
import time
from kopf import cli
from mizar.common.wf_param import *
from mizar.dp.mizar.workflows.vpcs.triggers import *
from mizar.dp.mizar.workflows.nets.triggers import *
from mizar.dp.mizar.workflows.dividers.triggers import *
from mizar.dp.mizar.workflows.bouncers.triggers import *
from mizar.dp.mizar.workflows.droplets.triggers import *
from mizar.dp.mizar.workflows.endpoints.triggers import *
from mizar.dp.mizar.workflows.builtins.services.triggers import *
from mizar.dp.mizar.workflows.builtins.nodes.triggers import *
from mizar.dp.mizar.workflows.builtins.pods.triggers import *
import grpc
from google.protobuf import empty_pb2
from concurrent import futures
from mizar.proto import vpcs_pb2_grpc as vpcs_pb2_grpc
from mizar.proto import nets_pb2_grpc as nets_pb2_grpc
from mizar.dp.mizar.workflows.proxy_service.proxy_service import ProxyServer

logger = logging.getLogger()
LOCK: asyncio.Lock
POOL_WORKERS = 10


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

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=POOL_WORKERS))

    vpcs_pb2_grpc.add_VpcsServiceServicer_to_server(
        ProxyServer(), server
    )
    nets_pb2_grpc.add_NetsServiceServicer_to_server(
        ProxyServer(), server
    )

    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("Running Proxy Server!")
    start_time = time.time()

    run_workflow(wffactory().DropletOperatorStart(param=param))
    run_workflow(wffactory().DividerOperatorStart(param=param))

    run_workflow(wffactory().VpcOperatorStart(param=param))

    run_workflow(wffactory().BouncerOperatorStart(param=param))

    run_workflow(wffactory().NetOperatorStart(param=param))
    run_workflow(wffactory().EndpointOperatorStart(param=param))

    logger.info("Bootstrap time:  %s seconds ---" % (time.time() - start_time))

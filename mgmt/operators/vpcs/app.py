#!/usr/bin/python3

from operators.vpcs.vpcs_handlers import *

import asyncio
import kopf

LOCK: asyncio.Lock

@kopf.on.startup()
async def vpcs_startup_fn(logger, **kwargs):
	logger.info("vpcs global start!")
	global LOCK
	LOCK = asyncio.Lock()  # uses the running asyncio loop by default

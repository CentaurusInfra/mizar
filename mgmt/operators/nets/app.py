#!/usr/bin/python3

from operators.nets.nets_handlers import *


import asyncio
import kopf

LOCK: asyncio.Lock

@kopf.on.startup()
async def nets_startup_fn(logger, **kwargs):
	logger.info("nets global start!")
	global LOCK
	LOCK = asyncio.Lock()  # uses the running asyncio loop by default


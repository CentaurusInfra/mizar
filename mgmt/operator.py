#!/usr/bin/python3

from operators.app import *

import asyncio
import kopf

LOCK: asyncio.Lock

@kopf.on.startup()
async def startup_fn(logger, **kwargs):
	logger.info("global start!")
	global LOCK
	LOCK = asyncio.Lock()  # uses the running asyncio loop by default

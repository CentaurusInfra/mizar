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
	logger.info("Delete called")
	conn.root.delete(params)
	exit()


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



# SPDX-License-Identifier: MIT
# Copyright (c) 2022 The Authors.

# Authors: The Mizar Team

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

import os
import logging
import subprocess
from netaddr import *

logger = logging.getLogger("transit_test")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def run_cmd(cmd_list):
    result = subprocess.Popen(cmd_list, shell=True, stdout=subprocess.PIPE)
    text = result.stdout.read().decode()
    returncode = result.returncode
    return (returncode, text)


def run_cmd_text(cmd_list):
    result = subprocess.Popen(cmd_list, shell=True, stdout=subprocess.PIPE)
    text = result.stdout.read().decode().rstrip()
    return text


def do_common_tests(test, ep1, ep2):
    do_ping_test(test, ep1, ep2)
    do_http_hostname_test(test, ep1, ep2)
    do_tcp_hostname_test(test, ep1, ep2)
    do_udp_hostname_test(test, ep1, ep2)


def do_ping_test(test, ep1, ep2):
    logger.info(
        "-------Test {}: ping {} {} ------".format(type(test).__name__, ep1.name, ep2.name))
    test.assertTrue(ep1.do_ping(ep2))
    test.assertTrue(ep2.do_ping(ep1))


def do_http_hostname_test(test, ep1, ep2):
    logger.info("-------Test {}: HTTP hostname {} {} ------".format(
        type(test).__name__, ep1.name, ep2.name))
    test.assertTrue(ep1.do_curl_hostname(ep2))
    test.assertTrue(ep2.do_curl_hostname(ep1))


def do_tcp_hostname_test(test, ep1, ep2):
    logger.info(
        "-------Test {}: TCP hostname {} {} ------".format(type(test).__name__, ep1.name, ep2.name))
    test.assertTrue(ep1.do_tcp_hostname(ep2))
    test.assertTrue(ep2.do_tcp_hostname(ep1))


def do_udp_hostname_test(test, ep1, ep2):
    logger.info(
        "-------Test {}: UDP hostname {} {} ------".format(type(test).__name__, ep1.name, ep2.name))
    test.assertTrue(ep1.do_udp_hostname(ep2))
    test.assertTrue(ep2.do_udp_hostname(ep1))

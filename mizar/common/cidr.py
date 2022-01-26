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

import ipaddress
import logging
from mizar.common.constants import *

logger = logging.getLogger()

class Cidr:
    def __init__(self, prefixlen, ip):
        """
        Defines an IPv4 CIDR block
        """
        self.prefixlen = prefixlen
        self.ip = ip
        self.ipnet = ipaddress.ip_network(
            "{}/{}".format(self.ip, self.prefixlen))
        self.subnets = self.ipnet.subnets(new_prefix=CONSTANTS.SUBNETS_NEW_PREFIX)

        self._hosts = set()
        self.gw = self.get_ip(1)
        self.allocated = set()

    @property
    def hosts(self):

        pool = next(self.subnets)
        # Avoid allocate special ip addresses such as net ip and gateway ip.
        pool_hosts_set = set(pool.hosts())
        pool_hosts_set.discard(ipaddress.IPv4Address(self.ip))
        pool_hosts_set.discard(ipaddress.IPv4Address(self.gw))
        while len(pool_hosts_set) == 0:
            pool = next(self.subnets)
            pool_hosts_set = set(pool.hosts())
            pool_hosts_set.discard(ipaddress.IPv4Address(self.ip))
            pool_hosts_set.discard(ipaddress.IPv4Address(self.gw))
        self._hosts.update(pool_hosts_set)
        return self._hosts

    def get_ip(self, idx):
        return self.ipnet[idx]

    def get_hosts(self):
        return self.hosts

    def allocate_ip(self):
        ip = self.hosts.pop()
        # TODO: bad hack, search the list and remove it!!
        while ip in self.allocated:
            ip = self.hosts.pop()
        self.allocated.add(ip)
        logger.info("ip {} is allocated. Currently there are {} ip addresses allocated under {}/{}."
            .format(ip, len(self.allocated), self.ip, self.prefixlen))
        return str(ip)

    def mark_ip_as_allocated(self, ip):
        self.allocated.add(ipaddress.IPv4Address(ip))

    def deallocate_ip(self, ip):
        ip = ipaddress.IPv4Address(ip)
        if ip in self.hosts:
            if ip in self.allocated:
                self.allocated.remove(ip)
            ip = self._hosts.add(ip)

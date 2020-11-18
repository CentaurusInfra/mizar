# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Hong Chang   <@Hong-Chang>

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

class CidrNetworkPolicy:
    def __init__(self, vni, localIP, cidr, cidrLength, policyBitValue, cidrType):
        self.vni = vni
        self.localIP = localIP
        self.cidr = cidr
        self.cidrLength = cidrLength
        self.policyBitValue = policyBitValue
        self.cidrType = cidrType
    def getCidrTypeInt(self):
        if self.cidrType == "NoExcept":
            return 0
        elif self.cidrType == "WithExcept":
            return 1
        else:
            return 2


class PortNetworkPolicy:
    def __init__(self, vni, localIP, protocol, port, policyBitValue):
        self.vni = vni
        self.localIP = localIP
        self.protocol = protocol
        self.port = port
        self.policyBitValue = policyBitValue

    def getProtocolInt(self):
        if self.protocol == "TCP":
            return 0
        elif self.protocol == "UDP":
            return 1
        else:
            return 2

class EndpointEnforced:
    def __init__(self, vni, ip):
        self.vni = vni
        self.ip = ip
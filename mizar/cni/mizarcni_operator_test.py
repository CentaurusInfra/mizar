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
import logging
import json
import os
import uuid
from mizar.daemon.interface_service import InterfaceServiceClient
from mizar.proto.interface_pb2 import *
from mizar.common.common import *

pod_id = PodId(
    k8s_pod_name="name",
    k8s_namespace="namespace",
    k8s_pod_tenant="tenant"
)

interface_id = InterfaceId(pod_id=pod_id, interface="eth0")

interface_address = InterfaceAddress(version="4",
                                     ip_address="10.0.0.2",
                                     ip_prefix="32",
                                     gateway_ip="10.0.0.1",
                                     mac="0a:0b:0c:0d:0e:0f",
                                     tunnel_id="3"
                                     )
droplet = SubstrateAddress(
    version="4", ip_address="172.0.0.1", mac="01:02:03:04:05:06")

bouncers = [SubstrateAddress(
    version="4", ip_address="172.0.0.2", mac="01:02:03:04:05:06"),
    SubstrateAddress(
    version="4", ip_address="172.0.0.3", mac="02:02:03:04:05:06"),
    SubstrateAddress(
    version="4", ip_address="172.0.0.4", mac="03:02:03:04:05:06")]

pod_name = get_pod_name(interface_id.pod_id)
local_id = str(uuid.uuid3(uuid.NAMESPACE_URL, pod_name))[0:8]
veth_name = "eth-" + local_id
veth_peer = "veth-" + local_id
veth = VethInterface(name=veth_name, peer=veth_peer)

inputInterface = Interface(
    interface_id=interface_id,
    interface_type=InterfaceType.veth,
    pod_provider=PodProvider.K8S,
    veth=veth,
    address=interface_address,
    droplet=droplet,
    bouncers=bouncers,
    status=InterfaceStatus.init
)

interfaces = InterfacesList(interfaces=[inputInterface])

interface = InterfaceServiceClient("localhost").ProduceInterfaces(interfaces)

print("RemoveInterfaces Input: {}".format(interface))

removeList = InterfaceServiceClient("localhost").RemoveInterfaces(interface)

print("removeList {}".format(removeList))

interface_id = InterfaceId(pod_id=pod_id, interface="eth0")

pod_name = get_pod_name(interface_id.pod_id)

consumedList = InterfaceServiceClient("localhost").ConsumeInterfaces(interface.interfaces[0].interface_id)

print("Consumed {}".format(consumedList))

deleteInput = interface.interfaces[0].interface_id
print("DeleteInterfaces input: {}".format(deleteInput))

deletedList = InterfaceServiceClient("localhost").DeleteInterfaces(interface.interfaces[0].interface_id)

print("Deleted {}".format(deletedList))

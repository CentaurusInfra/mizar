# SPDX-License-Identifier: MIT
# Copyright (c) 2021 The Authors.

# Authors: Jun Shao <@jshaofuturewei

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

import logging
from mizar.common.common import *

logger = logging.getLogger()

def get_cluster_gateway_host_ip(core_api):
    # Read gateway_host_ip from configmap
    cluster_gateway_config = kube_read_config_map(core_api,  "cluster-gateway-config", "default")
    gateway_host_ip = ""
    if cluster_gateway_config:
        gateway_host_ip = cluster_gateway_config.data["gateway_host_ip"]
        logger.info("The gateway host ip is {}".format(gateway_host_ip))
    else:
        logger.info("No gateway host is configured.")
    return gateway_host_ip

def get_cluster_gateway_droplet(droplets, cluster_gateway_host_ip):
    cluster_gateway_droplet = ""
    for dd in droplets:
        if dd.ip == cluster_gateway_host_ip:
            cluster_gateway_droplet = dd
            logger.info("A droplet {} has been added as cluster gateway.".format(dd.ip))
    return cluster_gateway_droplet

def get_remote_cluster_droplet(cluster_gateway_droplet, subnets, bouncer_subnet):
    remote_deployed_subnet_ips = set()
    for subnet in subnets.values():
        if subnet.remote_deployed == True:
            remote_deployed_subnet_ips.add(subnet.ip)
            logger.info("A subnet ip {} for subnet {} has been added.".format( subnet.ip, subnet.name))
    if bouncer_subnet in remote_deployed_subnet_ips:
         logger.info("remote deployed subnet, using cluster gateway droplet {}".format(cluster_gateway_droplet.ip))
         return cluster_gateway_droplet
    return ""

def get_remote_cluster_bouncer_droplet_with_cluster_config(core_api, store, droplets, bouncer):
    cluster_gateway_host_ip = get_cluster_gateway_host_ip(core_api)
    remote_cluster_bouncer_droplet = ""
    if cluster_gateway_host_ip != "":
        cluster_gateway_droplet = get_cluster_gateway_droplet(droplets, cluster_gateway_host_ip)
        if cluster_gateway_droplet != "":
            droplets.remove(cluster_gateway_droplet)
            subnets = store.get_nets_in_vpc(bouncer.vpc)
            remote_cluster_bouncer_droplet = get_remote_cluster_droplet(cluster_gateway_droplet, subnets, bouncer.get_nip())
    return remote_cluster_bouncer_droplet

def remove_cluster_gateway_droplet_with_cluster_config(core_api, droplets):
    cluster_gateway_host_ip = get_cluster_gateway_host_ip(core_api)
    cluster_gateway_droplet = ""
    if cluster_gateway_host_ip != "":
        cluster_gateway_droplet = get_cluster_gateway_droplet(droplets, cluster_gateway_host_ip)

    if cluster_gateway_droplet != "":
        droplets.remove(cluster_gateway_droplet)


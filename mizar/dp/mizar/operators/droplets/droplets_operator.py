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

import logging
import random
from mizar.common.constants import *
from mizar.common.common import *
from kubernetes import client, config
from mizar.obj.droplet import Droplet
from mizar.obj.bouncer import Bouncer
from mizar.obj.divider import Divider
from mizar.daemon.droplet_service import DropletClient
from mizar.store.operator_store import OprStore

logger = logging.getLogger()


class DropletOperator(object):
    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super(DropletOperator, cls).__new__(cls)
            cls._init(cls, **kwargs)
        return cls._instance

    def _init(self, **kwargs):
        logger.info(kwargs)
        self.store = OprStore()
        config.load_incluster_config()
        self.obj_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()
        self.bootstrapped = False

    def query_existing_droplets(self):
        def list_droplet_obj_fn(name, spec, plurals):
            logger.info("Bootstrapped droplet {}".format(name))
            d = Droplet(name, self.obj_api, self.store, spec)
            if d.status == OBJ_STATUS.droplet_status_provisioned:
                self.store_update(d)

        kube_list_obj(self.obj_api, RESOURCES.droplets, list_droplet_obj_fn)
        self.bootstrapped = True

    def is_bootstrapped(self):
        return self.bootstrapped

    def get_droplet_tmp_obj(self, name, spec):
        return Droplet(name, self.obj_api, None, spec)

    def get_droplet_stored_obj(self, name, spec):
        return Droplet(name, self.obj_api, self.store, spec)

    def store_get_by_ip(self, ip):
        return self.store.get_droplet_by_ip(ip)

    def store_get_by_main_ip(self, ip):
        return self.store.get_droplet_by_main_ip(ip)

    def set_droplet_provisioned(self, droplet):
        droplet.set_status(OBJ_STATUS.droplet_status_provisioned)
        droplet.update_obj()

    def store_update(self, droplet):
        self.store.update_droplet(droplet)

    def on_droplet_provisioned(self, body, spec, **kwargs):
        name = kwargs['name']
        logger.info(
            "Droplet on_droplet_provisioned {} with spec: {}".format(name, spec))
        d = Droplet(name, self.obj_api, self.store, spec)
        self.store.update_droplet(d)

    def assign_bouncer_droplet(self, bouncer):
        droplets = set(self.store.get_all_droplets())
        if len(droplets) == 0:
            return False
        # Read portal_host_ip from configmap
        portal_host_ip = get_portal_host(self.core_api)
        subnets = self.store.get_nets_in_vpc(bouncer.vpc)
        # remove portal hosts from the droplet set
        portal_droplet = ""
        external_subnet_ips = set()
        for subnet in subnets.values():
            if subnet.external:
                external_subnet_ips.add(subnet.ip)
                logger.info("A subnet ip {} for subnet {} has been added.".format( subnet.ip, subnet.name))

        for dd in droplets:
            if dd.ip == portal_host_ip:
                portal_droplet = dd
                logger.info("A droplet {} has been added as portal.".format(dd.ip))

        if portal_droplet != "":
            droplets.remove(portal_droplet)
            logger.info("The portal droplet {} has been removed.".format(portal_droplet))

        if bouncer.get_nip() in external_subnet_ips and portal_droplet != "":
            # for external subnets, use the portal host instead of picking a host as bouncer
            d = portal_droplet
            logger.info("external subnet, using portal droplet {}".format(d.ip))
        else:
            d = random.sample(droplets, 1)[0]

        bouncer.set_droplet(d)
        return True

    def assign_divider_droplet(self, divider):
        droplets = set(self.store.get_all_droplets())
        if len(droplets) == 0:
            return False

        # Read portal_host_ip from configmap
        portal_host_ip = get_portal_host(self.core_api)

        portal_droplet = ""
        for dd in droplets:
            if dd.ip == portal_host_ip:
                portal_droplet = dd
                logger.info("The portal droplet {} has been added.".format(dd.ip))
        if portal_droplet != "":
            droplets.remove(portal_droplet)

        # All the droplets have been removed as portal host droplet
        if len(droplets) == 0:
            return False

        d = random.sample(droplets, 1)[0]
        divider.set_droplet(d)
        return True

    def on_delete(self, body, spec, **kwargs):
        name = kwargs['name']

    def create_droplet(self, ip):
        try:
            clnt = DropletClient(ip)
            info = clnt.GetDropletInfo()
        except:
            return False
        spec = {
            'main_ip': ip,
            'ip': info.ip,
            'mac': info.mac,
            'itf': info.itf,
            'status': OBJ_STATUS.droplet_status_init
        }
        droplet = Droplet(info.name, self.obj_api, self.store, spec)
        droplet.create_obj()
        return True

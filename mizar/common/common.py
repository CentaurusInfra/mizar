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

import subprocess
import ctypes
import logging
import luigi
import datetime
import dateutil.parser
from kubernetes import watch, client
from ctypes.util import find_library
from mizar.common.constants import *
from pathlib import Path
_libc = ctypes.CDLL(find_library('c'), use_errno=True)

logger = logging.getLogger()


def run_cmd(cmd):
    result = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    text = result.stdout.read().decode()
    returncode = result.returncode
    return (returncode, text)


def get_iface_index(name, iproute):
    intfs = iproute.link_lookup(ifname=name)
    if len(intfs) == 0:
        return -1
    return intfs[0]


def get_iface_mac(idx, iproute):
    for (attr, val) in iproute.get_links(int(idx))[0]['attrs']:
        if attr == 'IFLA_ADDRESS':
            return val
    return None


def _nsfd(pid, ns_type):
    return Path('/proc') / str(pid) / 'ns' / ns_type


def host_nsenter(pid=1):
    _host_nsenter('mnt', pid)
    _host_nsenter('ipc', pid)
    _host_nsenter('net', pid)
    _host_nsenter('pid', pid)
    #_host_nsenter('user', pid)
    _host_nsenter('uts', pid)


def _host_nsenter(ns_type, pid=1):
    pid = pid

    target_fd = _nsfd(pid, ns_type).open()
    target_fileno = target_fd.fileno()

    if _libc.setns(target_fileno, 0) == -1:
        e = ctypes.get_errno()
        raise Exception(
            'namespace switch {} {} error {}'.format(pid, ns_type, e))
        target_fd.close()


def kube_create_obj(obj):
    try:
        body = obj.obj_api.get_namespaced_custom_object(
            group="mizar.com",
            version="v1",
            namespace="default",
            plural=obj.get_plural(),
            name=obj.get_name())
        spec = body['spec']
        obj.set_obj_spec(spec)
    except:
        body = {
            "apiVersion": "mizar.com/v1",
            "kind": obj.get_kind(),
            "metadata": {
                "name": obj.get_name()
            },
            "spec": obj.get_obj_spec()
        }

        body['spec']['createtime'] = datetime.datetime.now().isoformat()
        logger.info("Init {} at {}".format(
            obj.get_name(), body['spec']['createtime']))

        obj.obj_api.create_namespaced_custom_object(
            group="mizar.com",
            version="v1",
            namespace="default",
            plural=obj.get_plural(),
            body=body,
        )
        logger.debug("Created {} {}".format(obj.get_kind(), obj.get_name()))
    obj.store_update_obj()


def kube_update_obj(obj):
    get_body = True
    while get_body:
        body = obj.obj_api.get_namespaced_custom_object(
            group="mizar.com",
            version="v1",
            namespace="default",
            plural=obj.get_plural(),
            name=obj.get_name())

        spec = obj.get_obj_spec()

        if 'provisiondelay' not in spec or spec['provisiondelay'] == "":
            if 'createtime' in body['spec'] and spec['status'] == OBJ_STATUS.obj_provisioned:
                spec['createtime'] = body['spec']['createtime']
                now = datetime.datetime.now()

                created = dateutil.parser.parse(body['spec']['createtime'])
                delay = now - created
                spec['provisiondelay'] = str(delay.total_seconds())
                logger.info("Provisioned {} at {}, delay {} / {}".format(obj.get_name(),
                                                                         now, delay.total_seconds(), spec['provisiondelay']))

        body['spec'] = spec

        try:
            obj.obj_api.patch_namespaced_custom_object(
                group="mizar.com",
                version="v1",
                namespace="default",
                plural=obj.get_plural(),
                name=obj.name,
                body=body)
            obj.store_update_obj()
            get_body = False
        except:
            logger.debug("Retry updating {} {}".format(
                obj.get_kind(), obj.get_name()))
            get_body = True


def kube_delete_obj(obj):
    try:
        obj.obj_api.delete_namespaced_custom_object(
            group="mizar.com",
            version="v1",
            namespace="default",
            plural=obj.get_plural(),
            name=obj.name,
            body=client.V1DeleteOptions(),
            propagation_policy="Orphan")
    except:
        logger.debug("Failed to delete {} {}".format(
            obj.get_kind(), obj.get_name()))


def kube_watch_obj(obj, watch_callback):
    watcher = watch.Watch()
    stream = watcher.stream(obj.obj_api.list_namespaced_custom_object,
                            group="mizar.com",
                            version="v1",
                            namespace="default",
                            plural=obj.get_plural(),
                            field_selector="metadata.name={}".format(
                                obj.get_name()),
                            watch=True
                            )

    for event in stream:
        name = event['object']['metadata']['name']
        if name == obj.name:
            spec = event['object']['spec']
            obj.set_obj_spec(spec)
            obj.store_update_obj()
        if watch_callback(event, obj):
            watcher.stop()
            return


def kube_list_obj(obj_api, plurals, list_callback):
    response = obj_api.list_namespaced_custom_object(
        group="mizar.com",
        version="v1",
        namespace="default",
        plural=plurals,
        watch=False)
    items = response['items']
    for v in items:
        name = v['metadata']['name']
        spec = v['spec']
        list_callback(name, spec, plurals)


def kube_get_service_spec(core_api, service_name, service_namespace, get_callback):
    response = core_api.read_namespaced_service(
        name=service_name,
        namespace=service_namespace
    )
    logger.info(response)
    logger.info(response.spec)
    logger.info(response.spec.cluster_ip)
    get_callback(response.spec)


def get_spec_val(key, spec, default=""):
    return default if key not in spec else spec[key]


def run_workflow(task):
    luigi.build([task], detailed_summary=False)


def get_pod_name(pod_id):
    return pod_id.k8s_pod_name + '-' + pod_id.k8s_namespace + '-' + pod_id.k8s_pod_tenant


def get_itf_name(itf):
    return get_pod_name(itf.pod_id) + '-' + itf.interface

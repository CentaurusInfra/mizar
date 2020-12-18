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

from kubernetes import client
from mizar.common.kubernetes_util import *
from mizar.common.networkpolicy_data_util import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.networkpolicies.networkpolicies_operator import *

endpoint_opr = EndpointOperator()
networkpolicy_opr = NetworkPolicyOperator()

def handle_networkpolicy_create_update(name, pod_label_dict, policy_types):
    pods = list_pods_by_labels(pod_label_dict)

    has_ingress = "Ingress" in policy_types
    has_egress = "Egress" in policy_types

    if not has_ingress and not has_egress:
        return

    for pod in pods.items:
        pod_name = pod.metadata.name
        eps = endpoint_opr.store.get_eps_in_pod(pod_name)
        for ep in eps.values():
            if has_ingress:
                if name not in ep.ingress_networkpolicies:
                    ep.add_ingress_networkpolicy(name)
                data_for_networkpolicy_ingress = generate_data_for_networkpolicy_ingress(ep)
            if has_egress:
                if name not in ep.egress_networkpolicies:
                    ep.add_egress_networkpolicy(name)
                data_for_networkpolicy_egress = generate_data_for_networkpolicy_egress(ep)
            data_for_networkpolicy = {
                "old": {},
                "ingress": data_for_networkpolicy_ingress,
                "egress": data_for_networkpolicy_egress,
            }
            

def generate_data_for_networkpolicy_ingress(ep):
    data = init_data_for_networkpolicy()
    gress_type = "ingress"

    for networkpolicy_name in ep.ingress_networkpolicies:
        networkpolicy = networkpolicy_opr.get_networkpolicy(networkpolicy_name)
        fill_data_from_onegress(data, gress_type, networkpolicy)
    build_gressdata(data, ep)
    return data

def generate_data_for_networkpolicy_egress(ep):
    data = init_data_for_networkpolicy()
    gress_type = "egress"

    for networkpolicy_name in ep.egress_networkpolicies:
        networkpolicy = networkpolicy_opr.get_networkpolicy(networkpolicy_name)
        fill_data_from_onegress(data, gress_type, networkpolicy)
    build_gressdata(data, ep)
    return data
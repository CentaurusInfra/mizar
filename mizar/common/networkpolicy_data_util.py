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

from mizar.common.kubernetes_util import *
from cidr_trie import PatriciaTrie

def init_data_for_networkpolicy():
    data = {
        "indexed_policy_count": 0,
        "networkpolicy_map": {},
        "cidrs_map_no_except": {},
        "cidrs_map_with_except": {},
        "cidrs_map_except": {},
        "ports_map": {},
        "cidr_and_policies_map_no_except": {},
        "cidr_and_policies_map_with_except": {},
        "cidr_and_policies_map_except": {},
        "port_and_policies_map": {},
        "indexed_policy_map": {},
        "cidr_table_no_except": [],
        "cidr_table_with_except": [],
        "cidr_table_except": [],
        "port_table": [],
    }
    return data
            
def fill_data_from_onegress(data, gress_type, networkpolicy):
        network_policy_name = networkpolicy["metadata"]["name"]
        for index, onegress in enumerate(networkpolicy["spec"][gress_type]):
            indexed_policy_name = "{}_{}_{}".format(network_policy_name, gress_type, index)
            if network_policy_name not in data["networkpolicy_map"]:
                data["networkpolicy_map"][network_policy_name] = set()
            if indexed_policy_name not in data["networkpolicy_map"][network_policy_name]:
                data["networkpolicy_map"][network_policy_name].add(indexed_policy_name)
                data["indexed_policy_count"] += 1

            fill_cidrs_from_onegress(data, indexed_policy_name, gress_type, onegress)

def fill_cidrs_from_onegress(data, indexed_policy_name, gress_type, onegress):
    if indexed_policy_name not in data["ports_map"]:
        data["ports_map"][indexed_policy_name] = []
    for port in onegress["ports"]:
        data["ports_map"][indexed_policy_name].append("{}:{}".format(port["protocol"], port["port"]))

    if indexed_policy_name not in data["cidrs_map_no_except"]:
        data["cidrs_map_no_except"][indexed_policy_name] = []
    if indexed_policy_name not in data["cidrs_map_with_except"]:
        data["cidrs_map_with_except"][indexed_policy_name] = []
    if indexed_policy_name not in data["cidrs_map_except"]:
        data["cidrs_map_except"][indexed_policy_name] = []
    for gress_item in onegress["from" if gress_type == "ingress" else "to"]:
        if "ipBlock" in gress_item:
            if "except" in gress_item["ipBlock"]:
                data["cidrs_map_with_except"][indexed_policy_name].append(gress_item["ipBlock"]["cidr"])
                for except_cidr in gress_item["ipBlock"]["except"]:
                    data["cidrs_map_except"][indexed_policy_name].append(except_cidr)
            else:
                data["cidrs_map_no_except"][
                    indexed_policy_name].append(gress_item["ipBlock"]["cidr"])
        elif "namespaceSelector" in gress_item and "podSelector" in gress_item:
            raise NotImplementedError("Not implemented")
        elif "namespaceSelector" in gress_item:
            raise NotImplementedError("Not implemented")
        elif "podSelector" in gress_item:
            pods = list_pods_by_labels(gress_item["podSelector"]["matchLabels"])
            for pod in pods.items:
                data["cidrs_map_no_except"][indexed_policy_name].append("{}/32".format(pod.status.pod_ip))
        else:
            raise NotImplementedError("Not implemented for {}".format(gress_item))

def build_gressdata(data, ep):
    build_cidr_and_policies_map(data, "no_except")
    build_cidr_and_policies_map(data, "with_except")
    build_cidr_and_policies_map(data, "except")
    build_port_and_policies_map(data)
    build_indexed_policy_map(data)
    build_cidr_table(data, ep, "no_except")
    build_cidr_table(data, ep, "with_except")
    build_cidr_table(data, ep, "except")
    build_port_table(data, ep)

def build_cidr_and_policies_map(gressdata, cidr_type):
    cidr_map_name = "cidrs_map_" + cidr_type
    cidr_and_policies_map_name = "cidr_and_policies_map_" + cidr_type
    trie = PatriciaTrie()
    for indexed_policy_name, cidrs in gressdata[cidr_map_name].items():
        for cidr in cidrs:
            if cidr not in gressdata[cidr_and_policies_map_name]:
                gressdata[cidr_and_policies_map_name][cidr] = set()
            gressdata[cidr_and_policies_map_name][cidr].add(indexed_policy_name)
            trie.insert(cidr, gressdata[cidr_and_policies_map_name][cidr])
    for cidr, indexed_policy_names in gressdata[
            cidr_and_policies_map_name].items():
        found_cidr_map = trie.find_all(cidr)
        for found_cidr_tuple in found_cidr_map:
            if indexed_policy_names != found_cidr_tuple[1]:
                for foundPolicyName in found_cidr_tuple[1]:
                    indexed_policy_names.add(foundPolicyName)

def build_port_and_policies_map(gressdata):
        for indexed_policy_name, ports in gressdata["ports_map"].items():
            for port in ports:
                if port not in gressdata["port_and_policies_map"]:
                    gressdata["port_and_policies_map"][port] = set()
                gressdata["port_and_policies_map"][port].add(indexed_policy_name)

def build_indexed_policy_map(gressdata):
        bit = 1
        for _, indexed_policy_names in gressdata["networkpolicy_map"].items():
            for indexed_policy_name in indexed_policy_names:
                gressdata["indexed_policy_map"][indexed_policy_name] = bit
                bit <<= 1

def build_cidr_table(gressdata, ep, cidr_type):
        cidr_table_name = "cidr_table_" + cidr_type
        cidr_and_policies_map_name = "cidr_and_policies_map_" + cidr_type
        for cidr, indexed_policy_names in gressdata[cidr_and_policies_map_name].items():
            splitted_cidr = cidr.split("/")
            gressdata[cidr_table_name].append({
                "vni": ep.vni,
                "local_ip": ep.ip,
                "cidr": splitted_cidr[0],
                "cidr_length": int(splitted_cidr[1]),
                "bit_value": calculate_policy_bit_value(gressdata, indexed_policy_names),
            })

def calculate_policy_bit_value(gressdata, indexed_policy_names):
        policy_bit_value = 0
        for indexed_policy_name in indexed_policy_names:
            policy_bit_value += gressdata["indexed_policy_map"][indexed_policy_name]
        return policy_bit_value

def build_port_table(gressdata, ep):
        for port, indexed_policy_names in gressdata["port_and_policies_map"].items():
            splitted = port.split(":")
            gressdata["port_table"].append({
                "vni": ep.vni,
                "local_ip": ep.ip,
                "protocol": splitted[0],
                "port": splitted[1],
                "bit_value": calculate_policy_bit_value(gressdata, indexed_policy_names),
            })

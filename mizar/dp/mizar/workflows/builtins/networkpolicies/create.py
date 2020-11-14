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

import logging
import json
from cidr_trie import PatriciaTrie
from kubernetes import client
from mizar.common.workflow import *
from mizar.dp.mizar.operators.droplets.droplets_operator import *
from mizar.dp.mizar.operators.endpoints.endpoints_operator import *
from mizar.dp.mizar.operators.networkpolicies.networkpolicies_operator import *
from mizar.dp.mizar.operators.vpcs.vpcs_operator import *
from mizar.dp.mizar.operators.nets.nets_operator import *
from mizar.common.constants import *

logger = logging.getLogger()

droplet_opr = DropletOperator()
endpoint_opr = EndpointOperator()
networkpolicy_opr = NetworkPolicyOperator()
vpc_opr = VpcOperator()
net_opr = NetOperator()


class k8sNetworkPolicyCreate(WorkflowTask):
    def requires(self):
        logger.info("Requires {task}".format(task=self.__class__.__name__))
        return []

    def run(self):
        logger.info("Run {task}".format(task=self.__class__.__name__))
        networkPolicyName = self.param.name

        labelFilter = self.buildLabelFilter(self.param.spec["podSelector"]["matchLabels"])
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(watch=False, label_selector=labelFilter)

        for pod in pods.items:
            podName = pod.metadata.name
            eps = endpoint_opr.store.get_eps_in_pod(podName)
            for ep in eps.values():
                if networkPolicyName not in ep.networkpolicies:
                    ep.add_networkpolicy(networkPolicyName)
                    dataForNetworkPolicy = self.generateDataForNetworkPolicy(ep)
                    olddataForNetworkPolicy = ep.dataForNetworkPolicy
                    if len(olddataForNetworkPolicy) > 0:
                        dataForNetworkPolicy["old"] = olddataForNetworkPolicy
                    ep.set_dataForNetworkPolicy(dataForNetworkPolicy)
                    endpoint_opr.update_networkpolicy_per_endpoint(ep, dataForNetworkPolicy)

        self.finalize()

    def buildLabelFilter(self, matchLabels):
        strList = []
        for key in matchLabels:
            strList.append(key)
            strList.append("=")
            strList.append(matchLabels[key])
            strList.append(",")
        if len(strList) > 0:
            strList.pop()
        return "".join(strList)

    def generateDataForNetworkPolicy(self, ep):
        data = {
            "old": {},
            "ingress": {
                "indexedPolicyCount": 0,
                "networkPolicyMap": {},
                "cidrsMap_NoExcept": {},
                "cidrsMap_WithExcept": {},
                "cidrsMap_Except": {},
                "portsMap": {},
                "cidrAndPoliciesMap_NoExcept": {},
                "cidrAndPoliciesMap_WithExcept": {},
                "cidrAndPoliciesMap_Except": {},
                "portAndPoliciesMap": {},
                "indexedPolicyMap": {},
                "cidrTable_NoExcept": [],
                "cidrTable_WithExcept": [],
                "cidrTable_Except": [],
                "portTable": [],
            },
            "egress": {
                "indexedPolicyCount": 0,
                "networkPolicyMap": {},
                "cidrsMap_NoExcept": {},
                "cidrsMap_WithExcept": {},
                "cidrsMap_Except": {},
                "portsMap": {},
                "cidrAndPoliciesMap_NoExcept": {},
                "cidrAndPoliciesMap_WithExcept": {},
                "cidrAndPoliciesMap_Except": {},
                "portAndPoliciesMap": {},
                "indexedPolicyMap": {},
                "cidrTable_NoExcept": [],
                "cidrTable_WithExcept": [],
                "cidrTable_Except": [],
                "portTable": [],
            },
        }

        for networkPolicyName in ep.networkpolicies:
            networkPolicy = networkpolicy_opr.get_networkpolicy(networkPolicyName)
            self.fillDataByNetworkPolicy(data, networkPolicy)
        self.buildGressData(data, ep)
        return data

    def buildGressData(self, data, ep):
        if "ingress" in data:
            self.buildCidrAndPoliciesMap(data["ingress"], "NoExcept")
            self.buildCidrAndPoliciesMap(data["ingress"], "WithExcept")
            self.buildCidrAndPoliciesMap(data["ingress"], "Except")
            self.buildPortAndPoliciesMap(data["ingress"])
            self.buildIndexedPolicyMap(data["ingress"])
            self.buildCidrTable(data["ingress"], ep, "NoExcept")
            self.buildCidrTable(data["ingress"], ep, "WithExcept")
            self.buildCidrTable(data["ingress"], ep, "Except")
            self.buildPortTable(data["ingress"], ep)
        if "egress" in data:
            self.buildCidrAndPoliciesMap(data["egress"], "NoExcept")
            self.buildCidrAndPoliciesMap(data["egress"], "WithExcept")
            self.buildCidrAndPoliciesMap(data["egress"], "Except")
            self.buildPortAndPoliciesMap(data["egress"])
            self.buildIndexedPolicyMap(data["egress"])
            self.buildCidrTable(data["egress"], ep, "NoExcept")
            self.buildCidrTable(data["egress"], ep, "WithExcept")
            self.buildCidrTable(data["egress"], ep, "Except")
            self.buildPortTable(data["egress"], ep)

    def buildPortTable(self, gressData, ep):
        for port, indexedPolicyNames in gressData["portAndPoliciesMap"].items():
            splitted = port.split(":")
            gressData["portTable"].append({
                "vni": ep.vni,
                "localIP": ep.ip,
                "protocol": splitted[0],
                "port": splitted[1],
                "policyBitValue": self.calculatePolicyBitValue(gressData, indexedPolicyNames),
            })

    def buildCidrTable(self, gressData, ep, cidrType):
        cidrTableName = "cidrTable_" + cidrType
        cidrAndPoliciesMapName = "cidrAndPoliciesMap_" + cidrType
        for cidr, indexedPolicyNames in gressData[cidrAndPoliciesMapName].items():
            splittedCidr = cidr.split("/")
            gressData[cidrTableName].append({
                "vni": ep.vni,
                "localIP": ep.ip,
                "cidr": splittedCidr[0],
                "cidrLength": int(splittedCidr[1]),
                "policyBitValue": self.calculatePolicyBitValue(gressData, indexedPolicyNames),
            })

    def calculatePolicyBitValue(self, gressData, indexedPolicyNames):
        policyBitValue = 0
        for indexedPolicyName in indexedPolicyNames:
            policyBitValue += gressData["indexedPolicyMap"][indexedPolicyName]
        return policyBitValue

    def buildIndexedPolicyMap(self, gressData):
        bit = 1
        for policyName, indexedPolicyNames in gressData["networkPolicyMap"].items():
            for indexedPolicyName in indexedPolicyNames:
                gressData["indexedPolicyMap"][indexedPolicyName] = bit
                bit <<= 1

    def buildCidrAndPoliciesMap(self, gressData, cidrType):
        cidrMapName = "cidrsMap_" + cidrType
        cidrAndPoliciesMapName = "cidrAndPoliciesMap_" + cidrType
        trie = PatriciaTrie()
        for indexedPolicyName, cidrs in gressData[cidrMapName].items():
            for cidr in cidrs:
                if cidr not in gressData[cidrAndPoliciesMapName]:
                    gressData[cidrAndPoliciesMapName][cidr] = set()
                gressData[cidrAndPoliciesMapName][cidr].add(indexedPolicyName)
                trie.insert(cidr, gressData[cidrAndPoliciesMapName][cidr])
        for cidr, indexedPolicyNames in gressData[
                cidrAndPoliciesMapName].items():
            foundCidrMap = trie.find_all(cidr)
            for foundCidrTuple in foundCidrMap:
                if indexedPolicyNames != foundCidrTuple[1]:
                    for foundPolicyName in foundCidrTuple[1]:
                        indexedPolicyNames.add(foundPolicyName)

    def buildPortAndPoliciesMap(self, gressData):
        for indexedPolicyName, ports in gressData["portsMap"].items():
            for port in ports:
                if port not in gressData["portAndPoliciesMap"]:
                    gressData["portAndPoliciesMap"][port] = set()
                gressData["portAndPoliciesMap"][port].add(indexedPolicyName)

    #####################################

    def fillDataByNetworkPolicy(self, data, networkPolicy):
        hasIngress = "Ingress" in networkPolicy["spec"]["policyTypes"]
        hasEgress = "Egress" in networkPolicy["spec"]["policyTypes"]

        if hasIngress:
            gressType = "ingress"
            self.fillDataFromOneGress(data, gressType, networkPolicy)

        if hasEgress:
            gressType = "egress"
            self.fillDataFromOneGress(data, gressType, networkPolicy)

    def fillDataFromOneGress(self, data, gressType, networkPolicy):
        networkPolicyName = networkPolicy["metadata"]["name"]
        for index, onegress in enumerate(networkPolicy["spec"][gressType]):
            indexedPolicyName = "{}_{}_{}".format(networkPolicyName, gressType, index)
            if networkPolicyName not in data[gressType]["networkPolicyMap"]:
                data[gressType]["networkPolicyMap"][networkPolicyName] = set()
            if indexedPolicyName not in data[gressType]["networkPolicyMap"][networkPolicyName]:
                data[gressType]["networkPolicyMap"][networkPolicyName].add(indexedPolicyName)
                data[gressType]["indexedPolicyCount"] += 1

            self.getCidrsFromOnegress(data, indexedPolicyName, gressType, onegress)

    def getCidrsFromOnegress(self, data, indexedPolicyName, gressType, onegress):
        if indexedPolicyName not in data[gressType]["portsMap"]:
            data[gressType]["portsMap"][indexedPolicyName] = []
        for port in onegress["ports"]:
            data[gressType]["portsMap"][indexedPolicyName].append("{}:{}".format(port["protocol"], port["port"]))

        if indexedPolicyName not in data[gressType]["cidrsMap_NoExcept"]:
            data[gressType]["cidrsMap_NoExcept"][indexedPolicyName] = []
        if indexedPolicyName not in data[gressType]["cidrsMap_WithExcept"]:
            data[gressType]["cidrsMap_WithExcept"][indexedPolicyName] = []
        if indexedPolicyName not in data[gressType]["cidrsMap_Except"]:
            data[gressType]["cidrsMap_Except"][indexedPolicyName] = []
        for gressItem in onegress["from" if gressType == "ingress" else "to"]:
            if "ipBlock" in gressItem:
                if "except" in gressItem["ipBlock"]:
                    data[gressType]["cidrsMap_WithExcept"][indexedPolicyName].append(gressItem["ipBlock"]["cidr"])
                    for exceptCidr in gressItem["ipBlock"]["except"]:
                        data[gressType]["cidrsMap_Except"][indexedPolicyName].append(exceptCidr)
                else:
                    data[gressType]["cidrsMap_NoExcept"][
                        indexedPolicyName].append(gressItem["ipBlock"]["cidr"])
            elif "namespaceSelector" in gressItem and "podSelector" in gressItem:
                logger.info("Not implemented")
            elif "namespaceSelector" in gressItem:
                logger.info("Not implemented")
            elif "podSelector" in gressItem:
                labelFilter = self.buildLabelFilter(gressItem["podSelector"]["matchLabels"])
                v1 = client.CoreV1Api()
                pods = v1.list_pod_for_all_namespaces(watch=False, label_selector=labelFilter)
                for pod in pods.items:
                    data[gressType]["cidrsMap_NoExcept"][indexedPolicyName].append("{}/32".format(pod.status.host_ip))
            else:
                raise NotImplementedError("Not implemented for {}".format(gressItem))

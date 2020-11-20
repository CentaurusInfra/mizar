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

        policyTypes = self.param.spec["policyTypes"]
        hasIngress = "Ingress" in policyTypes
        hasEgress = "Egress" in policyTypes

        if not hasIngress and not hasEgress:
            self.finalize()
            return

        #endpointSet = set()
        for pod in pods.items:
            podName = pod.metadata.name
            eps = endpoint_opr.store.get_eps_in_pod(podName)
            for ep in eps.values():
                # endpointSet.add(ep.name)

                if hasIngress:
                    if networkPolicyName not in ep.ingressNetworkpolicies:
                        ep.add_ingress_networkpolicy(networkPolicyName)
                    dataForNetworkPolicyIngress = self.generateDataForNetworkPolicyIngress(ep)
                if hasEgress:
                    if networkPolicyName not in ep.egressNetworkpolicies:
                        ep.add_egress_networkpolicy(networkPolicyName)
                    dataForNetworkPolicyEgress = self.generateDataForNetworkPolicyEgress(ep)
                dataForNetworkPolicy = {
                    "old": {},
                    "ingress": dataForNetworkPolicyIngress,
                    "egress": dataForNetworkPolicyEgress,
                }
                # if networkPolicyName not in ep.networkpolicies:
                #     ep.add_networkpolicy(networkPolicyName)
                # dataForNetworkPolicy = self.generateDataForNetworkPolicy(ep)
                olddataForNetworkPolicy = ep.dataForNetworkPolicy
                if len(olddataForNetworkPolicy) > 0:
                    if len(olddataForNetworkPolicy["old"]) > 0 and olddataForNetworkPolicy["old"]["ingress"] == dataForNetworkPolicyIngress and olddataForNetworkPolicy["old"]["egress"] == dataForNetworkPolicyEgress:
                        continue

                    olddataForNetworkPolicy["old"] = {}
                    dataForNetworkPolicy["old"] = olddataForNetworkPolicy

                ep.set_dataForNetworkPolicy(dataForNetworkPolicy)
                logger.info("dataForNetworkPolicy:{}".format(dataForNetworkPolicy))
                endpoint_opr.update_networkpolicy_per_endpoint(ep, dataForNetworkPolicy)

        # for ep in endpoint_opr.store.eps_store.values():
        #     if ep.name not in endpointSet and networkPolicyName in ep.networkpolicies:
        #         ep.remove_networkpolicy(networkPolicyName)

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

    def generateDataForNetworkPolicyIngress(self, ep):
        data = {
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
        }
        gressType = "ingress"

        for networkPolicyName in ep.ingressNetworkpolicies:
            networkPolicy = networkpolicy_opr.get_networkpolicy(networkPolicyName)
            self.fillDataFromOneGress(data, gressType, networkPolicy)
        self.buildGressData(data, ep, gressType)
        return data

    def generateDataForNetworkPolicyEgress(self, ep):
        data = {
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
        }
        gressType = "egress"

        for networkPolicyName in ep.egressNetworkpolicies:
            networkPolicy = networkpolicy_opr.get_networkpolicy(networkPolicyName)
            self.fillDataFromOneGress(data, gressType, networkPolicy)
        self.buildGressData(data, ep, gressType)
        return data

    def buildGressData(self, data, ep, gressType):
        self.buildCidrAndPoliciesMap(data, "NoExcept")
        self.buildCidrAndPoliciesMap(data, "WithExcept")
        self.buildCidrAndPoliciesMap(data, "Except")
        self.buildPortAndPoliciesMap(data)
        self.buildIndexedPolicyMap(data)
        self.buildCidrTable(data, ep, "NoExcept")
        self.buildCidrTable(data, ep, "WithExcept")
        self.buildCidrTable(data, ep, "Except")
        self.buildPortTable(data, ep)

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
            if networkPolicyName not in data["networkPolicyMap"]:
                data["networkPolicyMap"][networkPolicyName] = set()
            if indexedPolicyName not in data["networkPolicyMap"][networkPolicyName]:
                data["networkPolicyMap"][networkPolicyName].add(indexedPolicyName)
                data["indexedPolicyCount"] += 1

            self.getCidrsFromOnegress(data, indexedPolicyName, gressType, onegress)

    def getCidrsFromOnegress(self, data, indexedPolicyName, gressType, onegress):
        if indexedPolicyName not in data["portsMap"]:
            data["portsMap"][indexedPolicyName] = []
        for port in onegress["ports"]:
            data["portsMap"][indexedPolicyName].append("{}:{}".format(port["protocol"], port["port"]))

        if indexedPolicyName not in data["cidrsMap_NoExcept"]:
            data["cidrsMap_NoExcept"][indexedPolicyName] = []
        if indexedPolicyName not in data["cidrsMap_WithExcept"]:
            data["cidrsMap_WithExcept"][indexedPolicyName] = []
        if indexedPolicyName not in data["cidrsMap_Except"]:
            data["cidrsMap_Except"][indexedPolicyName] = []
        for gressItem in onegress["from" if gressType == "ingress" else "to"]:
            if "ipBlock" in gressItem:
                if "except" in gressItem["ipBlock"]:
                    data["cidrsMap_WithExcept"][indexedPolicyName].append(gressItem["ipBlock"]["cidr"])
                    for exceptCidr in gressItem["ipBlock"]["except"]:
                        data["cidrsMap_Except"][indexedPolicyName].append(exceptCidr)
                else:
                    data["cidrsMap_NoExcept"][
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
                    data["cidrsMap_NoExcept"][indexedPolicyName].append("{}/32".format(pod.status.pod_ip))
            else:
                raise NotImplementedError("Not implemented for {}".format(gressItem))

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

        labelFilter = self.buildLabelFilter(
            self.param.spec["podSelector"]["matchLabels"])
        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(
            watch=False, label_selector=labelFilter)

        for pod in pods.items:
            podName = pod.metadata.name
            eps = endpoint_opr.store.get_eps_in_pod(podName)
            for ep in eps.values():
                if networkPolicyName not in ep.networkpolicies:
                    ep.add_networkpolicy(networkPolicyName)
                    self.generateDataForNetworkPolicy(ep)
                    endpoint_opr.send_networkpolicy_per_endpoint(
                        networkPolicyName, ep)

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
            "ingress": {
                "networkPolicyMap": {},
                "cidrsMap": {},
                "portsMap": {}
            },
            "egress": {
                "networkPolicyMap": {},
                "cidrsMap": {},
                "portsMap": {}
            },
        }

        for networkPolicyName in ep.networkpolicies:
            networkPolicy = networkpolicy_opr.get_networkpolicy(
                networkPolicyName)
            self.fillDataByNetworkPolicy(data, networkPolicy)
        self.buildData(data)
        breakpoint()
        return NetworkPolicyPerEndpoint()

    def buildData(self, data):
        if "ingress" in data:
            self.buildCidrAndPoliciesMap(data["ingress"])
            self.buildPortAndPoliciesMap(data["ingress"])
        if "egress" in data:
            self.buildCidrAndPoliciesMap(data["egress"])
            self.buildPortAndPoliciesMap(data["egress"])

    def buildCidrAndPoliciesMap(self, gressData):
        trie = PatriciaTrie()
        gressData["cidrAndPoliciesMap"] = {}
        for indexedPolicyName, cidrs in gressData["cidrsMap"].items():
            for cidr in cidrs:
                if cidr not in gressData["cidrAndPoliciesMap"]:
                    gressData["cidrAndPoliciesMap"][cidr] = set()
                gressData["cidrAndPoliciesMap"][cidr].add(indexedPolicyName)
                trie.insert(cidr, gressData["cidrAndPoliciesMap"][cidr])
        for cidr, indexedPolicyNames in gressData["cidrAndPoliciesMap"].items():
            foundCidrMap = trie.find_all(cidr)
            for foundCidrTuple in foundCidrMap:
                if indexedPolicyNames != foundCidrTuple[1]:
                    for foundPolicyName in foundCidrTuple[1]:
                        indexedPolicyNames.add(foundPolicyName)

    def buildPortAndPoliciesMap(self, gressData):
        gressData["portAndPoliciesMap"] = {}
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
            indexedPolicyName = "{}_{}_{}".format(
                networkPolicyName, gressType, index)
            if networkPolicyName not in data[gressType]["networkPolicyMap"]:
                data[gressType]["networkPolicyMap"][networkPolicyName] = []
            data[gressType]["networkPolicyMap"][networkPolicyName].append(
                indexedPolicyName)
            self.getCidrsFromOnegress(
                data, indexedPolicyName, gressType, onegress)

    def getCidrsFromOnegress(self, data, indexedPolicyName, gressType, onegress):
        if indexedPolicyName not in data[gressType]["portsMap"]:
            data[gressType]["portsMap"][indexedPolicyName] = []
        for port in onegress["ports"]:
            data[gressType]["portsMap"][indexedPolicyName].append(
                "{}:{}".format(port["protocol"], port["port"]))

        if indexedPolicyName not in data[gressType]["cidrsMap"]:
            data[gressType]["cidrsMap"][indexedPolicyName] = []
        for gressItem in onegress["from" if gressType == "ingress" else "to"]:
            if "ipBlock" in gressItem:
                data[gressType]["cidrsMap"][indexedPolicyName].append(
                    gressItem["ipBlock"]["cidr"])
            elif "namespaceSelector" in gressItem and "podSelector" in gressItem:
                logger.info("Not implemented")
            elif "namespaceSelector" in gressItem:
                logger.info("Not implemented")
            elif "podSelector" in gressItem:
                labelFilter = self.buildLabelFilter(
                    gressItem["podSelector"]["matchLabels"])
                v1 = client.CoreV1Api()
                pods = v1.list_pod_for_all_namespaces(
                    watch=False, label_selector=labelFilter)
                for pod in pods.items:
                    data[gressType]["cidrsMap"][indexedPolicyName].append(
                        "{}/32".format(pod.status.host_ip))
            else:
                raise NotImplementedError(
                    "Not implemented for {}".format(gressItem))

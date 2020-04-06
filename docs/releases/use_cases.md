<!--
SPDX-License-Identifier: MIT
Copyright (c) 2020 The Authors.

Authors: Sherif Abdelwahab <@zasherif>
         Phu Tran          <@phudtran>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:The above copyright
notice and this permission notice shall be included in all copies or
substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-->

Mizar shall support the following usage scenarios

## 1. VPC service of public cloud

**Target Users**: public cloud providers.

They use Mizar as their cloud networking solution, and build various network functions on top of Mizar. Example network functions include LB, NAT, Internet/VPN/VPC gateways, etc. They care about scalability, performance, monitoring, manageability, serviceability, hardware offloading, easy to support network functions, etc.

**Similar Solutions**: Proprietary solutions by public cloud vendors, like Azure VFP+Azure Virtual Network; GCE Andromeda; AWS VPC and Hyper-plane, etc.

## 2. Container clusters

**Target Users**: organizations that run Kubernetes, Mesos or Docker clusters.

They run small-size or medium-size container clusters in private data centers, in hosted Cloud VMs or in hosted container services (such as AWS EKS or Azure AKS). The cluster size is usually around hundreds of nodes. They care about easy deployment & configuration, performance, and good support for container networking policies, sidecars, etc.

**Similar solutions**: Flannel, Calico, Weave, Cilium, and service mesh products like Istio.

## 3. VM-based private IaaS cloud
**Target Users**: organizations that adopt OpenStack or VMware products.

They run VM clusters as IaaS service for their own private clouds, such as R&D Cloud. The cluster size varies from a few dozens to a few thousands. They care about performance, compatibility with other IaaS components, etc.

**Similar Solutions**: OpenStack Neutron; Commercial SDN solutions(software-based or hardware-based).

## 4. Large-scale private cloud
**Target Users**: large Internet companies.

They run large-scale clusters in their own data centers. For example JD.com operates large Kubernetes clusters with 10K+ nodes. Similar to the users in scenario #1, they care about scalability and performance of virtual networking. But they usually don't care too much about multi-tenancy isolation. Instead, they want to avoid overhead of overlay networking so that they can get best performance or bandwidth utilization.

**Similar Solutions**: Their home-brew solutions or enhanced version of open source products.

# Scenario-Feature Matrix

 "X" means a feature is required by the scenario.

|  Feature | Scenario #1  | Scenario #2  | Scenario #3  | Scenario #4   |
|----------|--------------|--------------|--------------|---|
|  Fix current perf Bottleneck   |       X       |      X        |      X        |    X  |
|           |   |   |   |   |
|  Complete VPC/subnet model |  X | X  |  X | X  |
|  Security Group |  X |   |  X |   |
|  Network ACL |   X|   |   |  X |
|  Routing Table |  X |   |   | X  |
|  Inter-VPC Routing |  X |   | X  |   |
|  DHCP and ARP Responder |  X |   |  X |   |
|  Scaled Endpoint     |      X        |        X      |              |   |
|  Fast Path           |      X        |   |   |   |
|  Auto-scale TS/TR           |      X        |   |   | X  |
|  Hardware Offloading           |         X     |   |   |   |
|  Integration with S/DNAT, LB, Gateway, etc           |         X     |   |  X |   |
|  Monitoring & Telemetry           |         X     |   |   |  X |
|  Live Migration & Live Update           |         X     |   |   |  X |
|  ARM Support and Optimization          |         X     |   |   |   |
|  P4 Support          |         X     |   |   |   |
|   |   |   |   |   |
|  CNI Plugin |   |  X |   |  X |
|  Container Network Polices |   | X   |   | X  |
|  Lightweight Control Plane |   | X   |   |   |
|  Label-based Selector|   |    | X  |   |
|  Containerized Deployment & Easy Configuration |   | X   |   | X  |
|   |   |   |   |   |
|   Neutron Plugin|   |   | X  |   |
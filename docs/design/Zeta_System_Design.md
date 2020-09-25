<!--
SPDX-License-Identifier: MIT
Copyright (c) 2020 The Authors.

Authors: Bin Liang <@liangbin888>

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

# Zeta System Design Document

Version 0.2

Table of Contents

[1. Introduction](#1-introduction)

[1.1 Purpose of the SDD](#11-purpose-of-the-sdd)

[1.2 Roles and Responsibilities](#12-roles-and-responsibilities)

[1.3 Terminology and Abbreviations](#13-terminology-and-abbreviations)

[2. General Overview and Design Guidelines/Approach](#2-general-overview-and-design-guidelinesapproach)

[2.1 General Overview](#21-general-overview)

[2.1.1 What is designed by Zeta project](#211-what-is-designed-by-zeta-project)

[2.1.2 What values Zeta project brings in](#212-what-values-zeta-project-brings-in)

[2.1.3 What use case is supported in Zeta's initial release](#213-what-use-case-is-supported-in-zetas-initial-release)

[2.2 Assumptions/Constraints/Risks](#22-assumptionsconstraintsrisks)

[2.2.1 Assumptions](#221-assumptions)

[2.2.2 Constraints](#222-constraints)

[2.2.3 Risks Analysis](#223-risks-analysis)

[3. Design Considerations](#3-design-considerations)

[3.1 Goals and Guidelines](#31-goals-and-guidelines)

[3.2 Development Methods & Contingencies](#32-development-methods--contingencies)

[4. System Architecture and Zeta Gateway Design](#4-system-architecture-and-zeta-gateway-design)

[4.1 System Architecture Diagram](#41-system-architecture-diagram)

[4.1.1 Zeta Control Plane](#411-zeta-control-plane)

[4.1.2 Zeta Data Plane](#412-zeta-data-plane)

[4.1.3 Zeta Networking Model](#413-zeta-networking-model)

[4.2 Hardware Architecture](#42-hardware-architecture)

[4.3 Software Architecture](#43-software-architecture)

[4.3.1 Logical View](#431-logical-view)

[4.3.2 Control Plane Enhancement](#432-control-plane-enhancement)

[4.3.3 Data Plane Enhancement](#433-data-plane-enhancement)

[4.3.4 Security Software Architecture](#434-security-software-architecture)

[4.3.5 Performance and Scalability Software Architecture](#435-performance-and-scalability-software-architecture)

[4.3.6 System Robustness](#436-system-robustness)

[4.4 Packaging and Deployment](#44-packaging-and-deployment)

[4.4.1 Best Practices](#441-best-practices)

[4.4.2 Prerequisites for deployment](#442-prerequisites-for-deployment)

[4.4.3 Zeta Control Plane installation](#443-zeta-control-plane-installation)

[4.4.4 Zeta Network Node Installation](#444-zeta-network-node-installation)

[4.4.5 Nova Compute Node Installation](#445-nova-compute-node-installation)

[5. External Interfaces](#5-external-interfaces)

[5.1 Interface Architecture](#51-interface-architecture)

[5.2 Interface Detailed Design](#52-interface-detailed-design)

[6. Operational Scenarios](#6-operational-scenarios)

[6.1 Compute Instance to instance](#61-compute-instance-to-instance)

[6.2 Compute Instance to instance Direct Path](#62-compute-instance-to-instance-direct-path)

[6.3 External Client Accesses Scaled Service](#63-external-client-accesses-scaled-service)

[6.4 Instance ARP Request](#64-instance-arp-request)

[6.5 ZGC Gateway Node Failure](#65-zgc-gateway-node-failure)

[6.6 Destination Compute Node Failure](#66-destination-compute-node-failure)

[6.7 Destination Regular Instance Failure](#67-destination-regular-instance-failure)

[6.8 Destination Service Instance Failure](#68-destination-service-instance-failure)

[Appendix A: Record of Changes](#_Toc490026795)

[Appendix B: Glossary](#_Toc396111629)

[Appendix C: Referenced Documents](#_Toc396111630)

[Appendix D: Review Comments](#_Toc396111631)

List of Figures

[Figure 1 - Zeta Gateway Service in Hosting Environments](#_Toc513123000)

[Figure 2 - OpenStack System Architecture with Zeta Gateway Service](#_Toc51312300)

[Figure 3 - Zeta Data Plane](#_Toc51759820)

[Figure 4 - Networking Model Transformation](#_Toc51759821)

[Figure 5 - Zeta Logical Architecture](#_Toc51312302)

[Figure 6 Deployment Model Best Practice](#_Toc51759823)

[Figure 7 Op Scenario: Between Instances](#_Toc51759824)

[Figure 8 Op Scenario: Access Service from Internet](#_Toc51759825)

[Figure 9 Op Scenario: Access Service from Internet](#_Toc51759826)

[Figure 10 Op Scenario: Instance ARP request](#_Toc51759827)

[Figure 11 Op Scenario: Zeta Gateway Node Failure](#_Toc51759828)

[Figure 12 Op Scenario: Destination Compute Node Failure](#_Toc51759829)

[Figure 13 Op Scenario: Destination Regular Instance Failure](#_Toc51759830)

[Figure 14 Op Scenario: Destination Service Instance Failure](#_Toc51759831)

List of Tables

[Table 1 Roles and Responsibilities](#_Toc51312298)

[Table 2 Terminology Cross Reference](#_Toc51312299)

[Table 3 Abbreviations](#_Toc51759840)

[Table 4 Zeta Phase I Key Success Factors](#_Toc51759841)

[Table 5 - Record of Changes](#_Toc444160465)

[Table 6 - Glossary](#_Ref441754492)

[Table 7 – Review Comments](#_Toc398804287)

## 1 Introduction

### 1.1 Purpose of the SDD

### 1.2 Roles and Responsibilities

The following table defines the Zeta Phase I Project roles and
responsibilities. This matrix also serves as the list of points of
contact for issues and concerns relating to the Zeta Phase I execution.

<span id="_Toc51312298" class="anchor"></span>Table 1 Roles and
Responsibilities

|                       |               |         |
| --------------------- | ------------- | ------- |
| Role                  | Name          | Contact |
| Product Owner         | Ying Xiong    |         |
| Project Manager       |               |         |
| Team Lead - Futurewei | Bin Liang     |         |
| Team Lead – USTC      | Gongming Zhao |         |
| Team Lead - Mizar     |               |         |
| Team Lead – Alcor     | Liguang Xie   |         |

Roles and Responsibilities

### 1.3 Terminology and Abbreviations

The following table lists the relevant terms commonly used in OpenStack
context and their corresponding terminology used in Zeta’s network
model.

<span id="_Toc51312299" class="anchor"></span>Table 2 Terminology Cross
Reference

|                   |                                                                         |                 |
| ----------------- | ----------------------------------------------------------------------- | --------------- |
| Term in OpenStack | Behavior Characteristics                                                | Zeta Term       |
| Project/Tenant    | To group and isolate resources from one another                         | Tenant          |
| Network           | Container of 1 or more subnets                                          | VPC             |
| Subnet            | L2 broadcast domain                                                     | Subnet          |
| Router            | Forward packets between subnets                                         | Divider (close) |
| Port              | Connection point to connect a single device to a subnet with IP and MAC | End Point       |
| Host Interface    |                                                                         | Droplet         |

Terminology Mapping

Next is a list of abbreviations used within this document.

<span id="_Toc51759840" class="anchor"></span>Table 3 Abbreviations

|              |                                                                            |
| ------------ | -------------------------------------------------------------------------- |
| Abbreviation | Literal Translation                                                        |
| TNW          | Tenant Network                                                             |
| PNW          | Provider Network                                                           |
| CNode        | Compute Node                                                               |
| ZNode        | Zeta Networking Node                                                       |
| ZGC          | Zeta Gateway Cluster                                                       |
| ZGS          | Zeta Gateway Service                                                       |
| vIP          | Service Virtual IP                                                         |
| FWD          | Zeta Gateway Service Forwarding Node                                       |
| FTN          | Zeta Gateway Service                                                       |
| OVS          | Open vSwitch                                                               |
| VM           | Tenant Virtual Compute Instance, including Virtual Machine, Container etc. |


## 2 General Overview and Design Guidelines/Approach

This section describes the principles and strategies to be used as
guidelines when designing and implementing the Zeta Gateway service.

### 2.1 General Overview

#### 2.1.1 What is designed by Zeta project

What we are designing in Zeta project is a common Networking Service Gateway (NSG for short) in
Cloud and Data Center virtual networking environment.

- To existing virtual networking infrastructure, Zeta NSG serves as a common proxy for offloaded
or additional virtual networking functions (VNF for short) in the form of XDP programs
- To those VNFs, Zeta NSG serves as a common hosting platform and framework to integrate them
into the overall virtual networking environment
- Zeta NSG offers performance, scalability and fault-tolerance for both Gateway service itself and
the VNFs it hosts
- Depends on capability and availability of hosted networking functions, Zeta NSG service extends
from most basic "Encapsulation proxy" all the way up to complete End-to-End networking service chain.
- Zeta NSG can operate in a standalone mode or extends its framework to Compute nodes for some or
 all its VNFs, in a distributed fashion

#### 2.1.2 What values Zeta project brings in

Compares to traditional central hosted virtual networking solutions, Zeta NSG solution offers:
- NSG clustering for scalability and reliability
- Unique Transparent Cluster Scaling to the NSG clients
- XDP/eBPF based VNF for maximal performance and minimal forwarding overhead

Compares to distributed virtual networking solutions, Zeta NSG solution offers:
- Support large compute node mesh, scaling up to tens of thousands
- Achieves same even better performance and latency characteristics
- XDP/eBPF based VNF for maximal performance and minimal forwarding overhead

#### 2.1.3 What use case is supported in Zeta's initial release

In the initial release, Zeta NSG will support following use case to demonstrate the framework with
a basic VNF in standalone fashion:
- Zeta Network Service Gateway framework
  - Deployment environment: OpenStack
  - Zeta Control plane
  - Zeta NSG on dedicated Network nodes
- VNF to offer: Encapsulation Proxy
  - Offering proxy service to Lookup and Encap the 1st packet in instance flow to its destination host
  - Enable compute host to host Direct Path for following packets in same flow
  - Support load balancing for tenant compute service  

### 2.2 Assumptions/Constraints/Risks

#### 2.2.1 Assumptions

1.  **Tenant network configurations and policies are persisted outside
    of Zeta Control Plane**  
    Zeta control plane follows declarative model and functions as
    stateless mechanism driver for OpenStack networking manager to
    implement tenant networking requirement. It relies on Networking
    manager like Alcor or Neutron to provide central repository for
    networking configuration, policy and telemetry data. This doesn’t
    prevent the usage of in-memory database within Zeta control plane
    components as local cache.

2.  **Underlay physical network and Compute nodes bridge (OVS) support
    VxLAN or Geneve tunnel protocol**  
    Zeta data plane functionality requires tunneled communication with
    Compute Node host bridges. Geneve protocol is preferred but since
    VxLAN is already used in most legacy OpenStack environment, Zeta
    Gateway service will support both for Tenant network. For private
    internal network inside Zeta Gateway Cluster, only Geneve protocol
    will be used because there is no interoperability concern and it
    offers best future proof extensibility.

3.  **Underlay physical network supports Jumbo frame**  
    In order to support 1500Bytes default MTU for compute instances,
    the underlay physical network segments hosting tenant network and
    Zeta Gateway network need to enable Jumbo frame support to avoid
    costly IP fragmentation at overlay end points. This doesn’t affect
    physical network segments hosting provider networks.

4.  **Compute Node OVS supports punt rules for user space processing**  
    Because of OVS limitation, the design may need user space assistance
    to handle special frames for in-band flow table operation, such
    as flow entry injection and invalidation. Neutron OVS doesn't support
    GPE extension or Geneve option header. Without this assumption, some
    Zeta networking feature will be limited. Preliminary research shows
    this assumption is very reasonable.

#### 2.2.2 Constraints

The Zeta Phase I Project’s goal is to deliver scaled and modular network
services in existing OpenStack IaaS solutions. Following constraints
have been identified which will impact and limit the design of the Zeta
service. These constraints are beyond the scope of the Zeta Phase I
Project but must be carefully factored into the system design. To date,
the following constraints have been identified:

  - Zeta Phase I must be backward compatible with existing OpenStack
    networking interfaces to provide transparent experience for both
    existing customers and other components in OpenStack eco system.

  - Zeta Phase I must avoid or minimize changes on existing compute
    nodes, especially to avoid requirement for kernel patch or upgrade.

  - Zeta Phase I relies on another open source project, code name
    “Alcor”, dependencies and scheduling commitment must meet Zeta
    Phase I initial release target which is end of year 2020.

#### 2.2.3 Risks Analysis

Zeta Phase I project is an Open Source project heavily relies on
community contribution cross multiple projects and teams. At the time of
writing, we have identified following teams identified as stakeholders
for the success of Zeta project:

  - Futurewei Zeta team

  - Mizar team

  - Alcor team

  - USTC team

Once we reached the design conclusion, we will have all teams committed
and mitigate any potential resource/schedule risk with weekly joint
scrum meeting.

We will also take a Test Driven and Early Integration approach to detect
and resolve cross-team issues in its earliest stage.

Special tie exists with Mizar project and the risk and remediation plan
will be addressed in Chapter 3.2.

## 3 Design Considerations

### 3.1 Goals and Guidelines

<span id="_Toc51759841" class="anchor"></span>Table 4 Zeta Phase I Key
Success Factors

<table>
<caption>Roles and Responsibilities</caption>
<tbody>
<tr class="odd">
<td>Success Factor</td>
<td>Expectation</td>
<td>Target</td>
</tr>
<tr class="even">
<td>On Boarding: VM Bring Up Latency (sec)</td>
<td>TBD</td>
<td>TBD</td>
</tr>
<tr class="odd">
<td>On Boarding: VM Bring Up Rate (vm/min @ 100, 1k, 10K VPC)</td>
<td>TBD</td>
<td>TBD</td>
</tr>
<tr class="even">
<td><p>Zeta Gateway Performance (Gb/s):</p>
<p>within host/subnet/tenant network/provider network &amp; with Internet</p></td>
<td>TBD</td>
<td>TBD</td>
</tr>
<tr class="odd">
<td>Network Robustness: Recover latency for Gateway node failure</td>
<td>TBD</td>
<td>TBD</td>
</tr>
<tr class="even">
<td>Network Robustness: Recover latency for VM migration</td>
<td>TBD</td>
<td>TBD</td>
</tr>
</tbody>
</table>

The design of Zeta Gateway service needs to meet following general guidelines:

1. Keep the design modular, easy to combine and scale
2. Avoid tight coupling and hard dependency with external environments
3. Forward thinking, avoid compromising on core design 

<span id="_Toc513123000" class="anchor"></span>Figure 1 - Zeta 
Gateway Service in Hosting Environments

![](.//png/Zeta_Diagrams_v1-Zeta_in_hosting_env.png)

### 3.2 Development Methods & Contingencies

Zeta Gateway Service interacts with Alcor and Compute nodes components
through control messages or data packets, there is no tight coupling.
This is not the case regarding Mizar project. Zeta Gateway software will
be built on top of Mizar Codebase so they are tightly coupled. Within
the Zeta phase I time frame, both projects will undergo active
development with different agenda and schedule. It is considered high
risky trying to coordinate between the two projects under the resource
and schedule constraints.

Zeta project will folk from Mizar at the right point and develop on its
own main branch. Critical fix or changes in Mizar project will be cherry
picked into Zeta repository.

It is expected that some extension/enhancement made in Zeta development
can be contributed back to Mizar project, but the decision and efforts
are not considered part of Zeta Phase I project.

## 4 System Architecture and Zeta Gateway Design

This section outlines the system architecture and design of Zeta Gateway
Service in OpenStack Cloud.

### 4.1 System Architecture Diagram

<span id="_Toc51312300" class="anchor"></span>Figure 2 - OpenStack
System Architecture with Zeta Gateway Service

![](.//png/Zeta_Diagrams_v1-System_Diagram.png)

In OpenStack system, Alcor networking manager (Alcor for short,
interchangeable with Neutron in the context of this document) manages
system-wide networking requests for Tenant compute instances, including
both in-host (within compute node) bridge networking and out-of-host
networking. For in-host bridge networking, Alcor deploys mechanism
drivers such as Open vSwitch (OVS for short). On the other hand, through
its plugin mechanism, Alcor relies on Zeta Control plane to deploy and
manage Zeta Gateway service for out-of-host tenant networking, include
hooking up to provider networks for public access and peering.

Even though Alcor is used throughout the document to represent the
top-level networking management service in OpenStack environment, Zeta
Gateway service will not have any hard coupling or dependency with any
particular flavor of OpenStack networking manager.

This design principle enables the following deployment scenarios but it
doesn’t mean all will be available in the initial phase of this project:

1.  Greenfield deployment: Zeta Gateway service can be deployed for all
    tenants/projects

2.  Brownfield deployment: Zeta Gateway service is used for only some
    networks in some projects, Alcor has/will use other alternative
    options for the rest of out-of-host networking needs

3.  Zeta Gateway service should work the same way with Alcor or
    alternative managers like Neutron.

Zeta Gateway Service provides overlay networking services for Tenant
compute instances such as Tenant VMs and/or Containers deployed on
OpenStack compute nodes. Shown as the purple blocks in OpenStack system
diagram above, Zeta Gateway Service is split into Zeta Control Plane and
Zeta Data Plane.

#### 4.1.1 Zeta Control Plane

Zeta Control Plane includes control and management logic for Zeta
Gateway service. It facilitates the interaction with the rest of
OpenStack control plane services, especially Alcor, through its
Northbound RESTful API and manages the life cycle of networking
functionalities deployed in Zeta Data Plane through its Southbound
Interface based on gRPC protocol. Zeta Control Plane services are
deployed within its own K8S cluster hosted on Zeta control nodes.

#### 4.1.2 Zeta Data Plane

<span id="_Toc51759820" class="anchor"></span>Figure 3 - Zeta Data Plane

![](.//png/Zeta_Diagrams_v1-Zeta_Data_Plane.png)

Zeta Data Plane is responsible for forwarding tenant virtual instance
traffic in and out of tenant and public networks. Zeta Data plane
presents itself to Tenant compute instances as a virtual gateway to a
flexible Tenant defined network, shown in above diagram as “Tenant
network Blueprint”. Tenants can define their virtual network as simple
as a local LAN segment or as complex as a full-fledged inter-connected
network across projects, remote sites and Internet. The next chapter
will go into details about how Zeta Gateway service transforms and
implements Tenant networking with built-in physical models, further
examples can be found in [Chapter 7 Operational
Scenarios.](#operational-scenarios)

Once Zeta Data Plane base image is deployed on dedicate Zeta network
nodes, it will register the Network node to Zeta Control Plane with its
node information and Zeta Gateway Cluster assignment. After the
registration, Zeta Control Plane will provision the Network Node as
either Forwarding node (FWD for short) or Distributed Flow Table node
(FTN for short) or both, depends on hardware capabilities and scaling
demand for the particular Network node type. To simplify the
architecture description, we will view FWD and FTN as separate nodes
from now on even though a single Zeta Network node can serve as both FWD
and FTN.

##### 4.1.2.1 FWD

In a nutshell, an FWD node serves as both the entry point and exist
point for a Tenant traffic flow (one way) in Zeta Gateway serve. The
main responsibilities for FWD nodes are:

1.  ARP responder

2.  Receiving Tenant traffic from compute nodes or external networks
    like remote VPN sites or Internet

3.  Lookup flow cache for Tenant traffic
    
    1.  If not found in local cache, query from FTN which may triggering
        flow creation on FTN
    
    2.  Add flow entry returned from FTN into local cache

4.  Act on the packet based on verdict from the matching flow entry
    cache:
    
    1.  Execute additional per packet networking functions (as M-XDP) as
        indicated in flow cache
    
    2.  Drop the packet and/or
    
    3.  Send ICMP packet back to packet sender
    
    4.  Modify the packet based on verdict context and send the packet
        out to next hop which should be either the compute host of
        destination instance, or provider network gateway towards
        external networks.

Normally there are two sets of FWDs within a given Zeta Gateway Cluster:
Tenant facing FWDs and Provider facing FWDs.

###### 4.1.2.1.1 Tenant Facing FWDs

The Tenant facing FWD nodes has one interface on Tenant network and
another interface on Zeta Gateway network. They are the ZGC entry points
for Tenant compute instances and will be populated to the Compute Node
if such Compute instances will be deployed.

###### 4.1.2.1.2 Provider facing FWDs

The Provider facing FWD nodes has one interface on Provider network and
another interface on Zeta Gateway network. They are the ZGC entry points
for packets coming from external networks through the attached Provider
network. For better throughput and reliability, multiple such FWDs can
be used to support Load Balancing, ECMP or Link aggregation depends on
the capability of physical router in the provider network. While in
theory Tenant facing FWDs don’t have a scaling out limit, maximal number
of Provider facing FWDs are often hard limited and won’t take part in
the elastic scaling of ZGC the same way as Tenant facing FWDs. This
factor is also considered when designing the data path logic. Some of
the forwarding workloads on these FWDs can be proxied by easily scalable
Tenant facing FWDs, avoiding their limited resources becoming
bottleneck. See chapter for a reference traffic flow.

##### 4.1.2.2 ZGC Load Balancing and Compute Node Direct Path 

In Zeta Phase I project, the design assumes OVS host bridge is deployed
on every Compute Node.

For simple flows such as those within a subnet, Compute node OVS bridge
may be able to carry on FWD’s responsibility \#4 after flow creation.
So, all the future packets in the flow can be modified at host OVS
bridge and sent to destination node directly, avoiding the hop to FWD.
This feature is referred to as “Direct Path” which further reduces the
networking overhead/latency for east-west traffics. But in order to make
this feature to work, there are a few concerns have to be addressed,
listed here:

1.  How to inject the newly created flow entry in Compute node OVS?
    
    1.  DFW sends the flow entry in band as optional header to Compute
        node OVS which then matches and updates flow tables in place.
        The preliminary research shows this may be a very challenging
        task for OVS. Supporting the optional header is also very risky
        in existing production environment. 
    
    2.  Alternatively, the flow entry can go through control plane. This
        approach addresses the issues with OVA in-place table change and
        optional header, but it introduces new scalability and latency
        issues as fast flow creation in data path will easily congest
        control channels, definitely a red flag.

    3.  A balanced approach would be passing OAM information in-band like
        option 1 but process it in user space like option 2, assuming punt
        rules can be added in OVS for such special frames. The risk of
        this approach is very minimal and latency is close to option 1. We
        will adopt this method in current design for Direct Path and other 
        Compute node side feature distribution.

2.  Similar issues are introduced for invalidation of these dynamic flow
    entries on Compute nodes as well.

    > Based on Option 3 approach, this concern can be addressed the same way.

3.  How to avoid Split-brain condition when Alcor owns Compute Node OVS?

    The user space handling of such special frames must coordinated with agent
    of OpenStack networking controller on each Compute Node, which is ACA for
    Alcor controller. Some conflict handling logic should be developed in ACA
    to merge or reject such modification from Zeta Gateway service.  

For robustness and on-demand performance, Zeta Control Plane will deploy
at least two FWDs for each Gateway service instance to form a cluster
referred to as Zeta Gateway Cluster in this document (ZGC for short).

By definition, ZGC follows administrative rules listed below:

  - Zeta Control Plane can create one or many ZGCs for isolation,
    maintenance or service differentiation

  - A Zeta Network Node is administratively assigned to one of the ZGCs

  - A ZGC will have at least two FWD nodes deployed with one or many FTN
    nodes

  - A ZGC will provide exclusive Zeta Gateway Service to one or many
    Tenant/Projects networks

When Compute Node OVS bridge receives an egress tenant packet from one
of its compute instances, it looks up the right ZGC it belongs to
locally, based on the Tenant/Project (VNI) the packet associated with.
Once identified the ZGC, it will further select one of its pre-populated
FWDs as proxy to tunnel the original packet through. This is called ZGC
Load Balancing which can achieve per-flow granularity.

Since ZGC can be horizontally scaled, the list of FWDs for a given ZGC
can change on the fly, affecting the ZGC Load Balancing logic described
above if the change is not propagated to all the compute nodes. This
creates a severe scalability issue if not addressed properly as there
can be hundreds even tens of thousands compute nodes served by each ZGC.
A novel solution for this problem has been developed and the detail will
be available in the short future.

##### 4.1.3 FTN And DFT

FTN nodes are internal Zeta Network Nodes within a ZGC. FTN offers
lookaside assistance to FWD hence they are not required to be attached
to the same Tenant network as Compute Nodes. Inter-connecting DFWs and
FDNs on an Isolated network avoids interfering between ZGC internal
traffic with Tenant traffics. It also allows fully customized
communication scheme without any compatibility issues with Compute Nodes
if needed, such as enabling Jumbo frame.

The main responsibilities for FTN nodes are:

1.  Building block for Distributed Flow Table (DFT for short), refer to
    \[1\] for DFT details
    
    1.  Forming replication chain (at least two) to implement redundancy
        for DFT
    
    2.  Multiple replication chain for scaling DFT partition

2.  For Tail FDN in DFT replication chains:
    
    1.  Respond to FWD for flow lookup request
    
    2.  Apply End-to-End forwarding and policy rules associated with the
        flow and populated the final verdicts in the flow entry during
        flow creation
    
    3.  DFT flow entry CRUD operation

#### 4.1.3 Zeta Networking Model

Before we dive further into the Zeta design, let’s take a look at Zeta
service from the user’s perspective.

In the context of OpenStack IaaS solution what we are targeting this
project to, the expected users are generally sysadmin or network admin
at either cloud provider level or Cloud Tenant level. In Day 0 and Day
1, Cloud provider Admins will have their Data Center’s physical
infrastructure ready and fully networked, similar to the simplified
architecture shown in Figure 1 above. Then they will deploy Zeta
components in servers designated as Zeta control nodes and network
nodes. The deployment detail will be covered in later chapters. Once
Zeta Gateway service is deployed as part of OpenStack IaaS offering,
cloud Provider expects Zeta to deliver flexible, efficient and highly
scalable overlay networking capabilities to their customers, in a
multi-tenant, multi-project flavor. From Day2 and beyond, Tenant admins
will login and blueprint their virtual networks for VMs, very similar to
what provider admins did in day0/day1 to connect their Server boxes into
physical networks.

So, we know both of these two kinds of users think and operate using the
same “networking concept”, derived from years of education and practice.
This is what’s natural to our users and we have no intention or power to
change that.

But, as we are building a service to actually implement the networking
blueprint in a virtual environment, we must understand the fundamental
differences with physical networking, to name a few:

  - Virtual networking is highly dynamic comparing to physical
    networking, which is not change very often, if ever at all

  - Virtual networking requires bringing up time in seconds rather than
    days and often weeks for physical networking

  - Virtual networking expecting elastic behavior like virtual
    computing, which is Never a reasonable expectation in physical
    networking world

In order to continue honoring the user’s old perspective for networking,
while designing a solution satisfying their new perspective for virtual
environment, a new networking model must be developed which can still
resemble the old concept.

<span id="_Toc51759821" class="anchor"></span>Figure 4 - Networking
Model Transformation

![](.//png/Zeta_Diagrams_v1-networking_logic_model_landscape.png)

From upper left conner of the above diagram, we can tell that OpenStack
is using a traditional network modeling language when describe and
construct its network. The steps following the purple arrow illustrate
how this traditional network model can be decomposed and transformed
into a simpler but much more efficient and elastic physical model in
Zeta.

Taking an analogy with a math function, the tradition model is like
executing the function line by line for each input to get an output,
while Zeta model is like fetch result from a looking up table. The huge
performance gain with upper-bounded latency are two key demands for
Cloud any IaaS solution.

With same analogy, we can pre-build the lookup table with all possible
inputs to achieve the ideal O(1) time complexity, but with significant
space cost. This is not acceptable in real systems hence Zeta takes a
“record once replay many times” approach, illustrated in step 3 above.
FTN\[1\] node inside Zeta Gateway will run the first packet in a flow
through required network functions (XDP programs in Zeta) and record the
result for the flow. Now the lookup table is built on-demand with only
active flows while still maintaining the O(1) complexity for the rest of
the flow.

In cases where the packet manipulation for a flow is simple, the flow
processing can be pushed to OVS on the initiating compute host,
resulting host to host direct communication we call direct path.

In this document, we will use logical networking model to explain
networking concepts from user’s perspective and use Zeta’s physical
networking model when we describe implementation details.

### 4.2 Hardware Architecture

### 4.3 Software Architecture

Zeta Gateway software leverages existing “Mizar” Open Source project as
control plane framework with extension and enhancement described in this
chapter. For Mizar project and its design documentation, please refer to
reference \[2\] for detail.

#### 4.3.1 Logical View

<span id="_Toc51312302" class="anchor"></span>Figure 5 - Zeta Logical
Architecture

![](.//png/Zeta_Diagrams_v1-Logical_Architecture.png)

The scope of Zeta Phase I design is colored Purple in Architecture
diagram above. We will leverage Open Source project “Alcor” for
networking service API proxy to the rest of OpenStack control plane.

Zeta control plane is based on the management service of Open Source
project “Mizar”. It will be extended to support new networking models in
Zeta and will be deployed in a standalone K8S cluster.

Zeta data plane will be the main focus for phase I development and it
will be hosted on dedicated network nodes.

Another important piece to cover is on compute node side. Although we
don’t expect system level changes there, we must make setup changes on
compute node OVS tables. This is required to support Zeta underlay
networking and on-demand flow injection.

#### 4.3.2 Control Plane Enhancement

##### 4.3.2.1 Zeta Server and Extended NBI

Mizar’s existing NBI through K8S API server is very K8S centric,
following a strict resource model for direct CRUD operation with
built-in components. This is absolutely needed to leverage K8S life
cycle management for custom resources Mizar defined for cloud
networking. But it would not necessary the best API for other
application/service to use for their networking purpose.

As explained in chapter 4.1, a logical model is more abstract and easier
to convey in order to achieve common perspective. Using low level APIs
with implementation specific details not only leads to confusion, it
also creates unnecessary adaptation work for any potential clients
trying to use the API.

With this consideration, Zeta will enhance API service with a new set of
APIs based on logical networking model matching the semantics user used
to define their network.

New backend “**Zeta Server**” will be developed to provide following
functionalities:

1.  Ingress service for Logical Model APIs

2.  Decompose/transform logic model into Zeta physical model represented
    by CRDs and map the relationships into in-memory DB/Graph for
    tracking

3.  Trigger workflows to coordinate CRUD requests using existing CRD
    APIs.

4.  Aggregate/compose CRDs status back to logical model and report back
    to API clients

##### 4.3.2.2 Zeta CRD Operator

Zeta physical model elements in data plane are managed by control plane
CRD operators. Some enhancement and extension are needed for OpenStack
deployment:

1.  Support multiple VLANs per host interface - Underlay L2 network for
    Tenant network may be flat or VLAN segmented. If the latter is the
    case, one node interface may connect to multiple physical networks.
    This is even more likely to happen for network nodes connecting
    tenant network with multiple provider networks like Internet, VPC
    peering and campus VPN. The underlay information should be passed to
    Zeta control plane when a network is created from Alcor. Droplet
    modeling may change from host interface association to underlay
    network association.

2.  Scaled End Point, see reference \[1\] for detail

3.  New CRDs for FWD and FTN, see reference \[1\] for detail

##### 4.3.2.3 Zeta Extended SBI

Zeta control plane places and provisions its data plane components on
network nodes through its Southbound Interface (SBI for short) . Current
plan for SBI is leveraging the existing gRPC channel between Mizar
manager and Mizar daemon. This should be sufficient for pushing control
logic to Zeta Network nodes but may cause timing issues if it’s used for
network telemetry data as well, especially risky in heavy production
environment. A Pub/Sub messaging mechanism should be considered for
telemetry data and better scaling, such as OpenStack’s AMQP service
based on RabbitMQ.

##### 4.3.2.4 Zeta Plugin for Alcor

This is the new plugin module installed with Alcor network manager. It
has following functionalities:

1.  Attach Zeta Gateway service as one of out-of-host networking
    controllers to Alcor

2.  Serve as a client to the new Zeta Logical Model APIs to proxy Alcor
    requests to Zeta Server

3.  Persist tenant network configuration and policy (If not done by
    Alcor server) assigned to Zeta

4.  Restore Zeta control plane after restart

##### 4.3.2.5 Alcor Control Agent (ACA)

This module runs on every compute node and needs to be enhanced to
support:

1.  Receive and store entry point list for each ZGC from Alcor Server
    during Compute Node provisioning.

2.  During compute instance provisioning, add OVS flow entry for
    instance’s default gateway VIP if it was not added before and fill
    the gateway VIP mapping bucket with the entry point list stored for
    the instance’s ZGC. Since no remote communication required for this
    step, the overhead for flow table update during instance on-boarding
    is negligible. To further reduce it to zero overhead, default flow
    entries to each ZGC can be pre-installed at compute node
    provisioning time. This design minimizes the default flow table
    loading time during VM on-boarding to almost ZERO and eliminates the
    costly flow distribution from Open Flow Controller, making large
    scale VPC bringing up a snap.

#### 4.3.3 Data Plane Enhancement

Zeta Gateway service’s data plane is implemented through XDP programs in
kernel for performance and modularity. We can leverage the existing
framework from Mizar compute node almost entirely and focus our effort
on new transit XDP logics.

#### 4.3.4 Security Software Architecture

The Zeta design would incorporate several security and integrity
controls to ensure that the system and its data are continually
protected. This is done through a multi-tiered approach to ensuring data
integrity is achieved through only authorized user functions and
assignments.

The first design consideration is user authorization or permissions.
Zeta should utilize existing OpenStack Identity service framework for
user and API authentication and authorization.

The Zeta design would also incorporate an audit trail capability to
track the history of change history, error identification, etc.

For the SBI gRPC channel between Zeta control plane and Zeta Network
node, authentication and encryption can be enabled as an administrative
configuration option.

For intra ZGC internal communication between FWDs and FTNs, the network
can be made totally isolated and authentication/encryption can be
enabled as configuration option.

The security capabilities will be provided in a phased approach.

#### 4.3.5 Performance and Scalability Software Architecture

Performance and Scalability are as important as functionality, if not
more, so they are evaluated and integrated in pretty much every aspect
of the design. Detailed concern and remediation are covered throughout
this document where it’s needed.

#### 4.3.6 System Robustness

Once deployed, Zeta gateway will provide foundation services to the rest
of OpenStack cloud. Robustness is a key factor for this project’s
success. Zeta Phase I project will provide following capabilities to
prevent catastrophic failures:

  - Zeta Control plane service instance can recover from restart without
    data plane interruption

  - Zeta Control plane service can recover from restart without data
    plane interruption

  - Zeta Control plane can recover from restart without data plane
    interruption, rely on Alcor/Neutron config push again =\> valid
    assumption?

  - Zeta Gateway cluster health monitoring and manual scaling

### 4.4 Packaging and Deployment

#### 4.4.1 Best Practices

<span id="_Toc51759823" class="anchor"></span>Figure 6 Deployment Model
Best Practice

![](.//png/Zeta_Diagrams_v1-Best_Practice_Networking.png)

1.  Use separate interfaces for Control/API network and tenant network

2.  Separate physical network segment for internal traffics within a
    Zeta Gateway cluster.

#### 4.4.2 Prerequisites for deployment

1.  OpenStack core services deployed and ready
    
    1.  Identity Service – Keystone
    
    2.  Compute Service – Nova
    
    3.  Networking Service – Alcor with Zeta plugin
    
    4.  (Optional) Web Front End – Horizon
    
    5.  (Optional) Image Service - Glance

2.  Minimal requirements for Zeta control nodes:
    
    1.  Minimal 3 nodes, 1 as K8S master and 2 as worker nodes
    
    2.  Minimal hardware configuration:
        
        1.  4 cores
        
        2.  RAM: 16 GB Fully Buffered
        
        3.  80GB 15,000 RPM Hard Drive
        
        4.  1x GE management port
        
        5.  1x GE for control network

3.  Minimal requirements for Zeta network nodes:
    
    1.  Minimal 6 nodes, 2 host FWD and 4 host FTN
    
    2.  Minimal hardware configuration:
        
        1.  4 cores
        
        2.  RAM: 16 GB Fully Buffered
        
        3.  40GB 15,000 RPM Hard Drive
        
        4.  1x GE management port
        
        5.  1x GE for control network
        
        6.  2x GE for Tenant network and Provider network

4.  Zeta Packages:

5.  Environment and Initial Configuration

#### 4.4.3 Zeta Control Plane installation

##### 4.4.3.1 K8S Cluster Setup

##### 4.4.3.2 Zeta Control Plan deployment

#### 4.4.4 Zeta Network Node Installation

#### 4.4.5 Nova Compute Node Installation

No Zeta specific changes are expected for Nova compute node
installation. Follow normal procedure as documented in OpenStack
Documentation.

## 5 External Interfaces

### 5.1 Interface Architecture

### 5.2 Interface Detailed Design

## 6 Operational Scenarios

### 6.1 Compute Instance to instance

<span id="_Toc51759824" class="anchor"></span>Figure 7 Op Scenario:
Between Instances

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_normal_between_instances.puml)

### 6.2 Compute Instance to instance Direct Path

<span id="_Toc51759825" class="anchor"></span>Figure 8 Op Scenario:
Between Instances

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_normal_between_instances_directpath.puml)

### 6.3 External Client Accesses Scaled Service

<span id="_Toc51759826" class="anchor"></span>Figure 9 Op Scenario:
Access Service from Internet

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_normal_internet_to_service.puml)

### 6.4 Instance ARP Request

<span id="_Toc51759827" class="anchor"></span>Figure 10 Op Scenario:
Instance ARP request

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_normal_arp_request.puml)

### 6.5 ZGC Gateway Node Failure

<span id="_Toc51759828" class="anchor"></span>Figure 11 Op Scenario: Zeta
Gateway Node Failure

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_failure_fwd.puml)

### 6.6 Destination Compute Node Failure

<span id="_Toc51759829" class="anchor"></span>Figure 12 Op Scenario:
Destination Compute Node Failure

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_failure_dest_host.puml)

### 6.7 Destination Regular Instance Failure

<span id="_Toc51759830" class="anchor"></span>Figure 13 Op Scenario:
Destination Regular Instance Failure

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_failure_dest_instance.puml)

### 6.8 Destination Service Instance Failure

<span id="_Toc51759831" class="anchor"></span>Figure 14 Op Scenario:
Destination Service Instance Failure

![](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/liangbin-pub/mizar/zeta/docs/design/puml/zeta_packet_farwarding_failure_dest_service_instance.puml)


<span id="_Toc490026795" class="anchor"></span>

## Appendix A: Record of Changes ##

<span id="_Toc444160465" class="anchor"></span>Table 5 - Record of
Changes

<table>
<caption>Record of Changes</caption>
<tbody>
<tr class="odd">
<td>Version Number</td>
<td>Date</td>
<td>Author/Owner</td>
<td>Description of Change</td>
</tr>
<tr class="even">
<td>0.1</td>
<td>09/15/2020</td>
<td>Bin Liang</td>
<td>Initial draft of Zeta SDD</td>
</tr>
<tr class="odd">
<td>0.2</td>
<td>09/21/2020</td>
<td>Bin Liang</td>
<td><p>Initial version for review, majority done, operational scenarios pending</p>
<p>Decisions to make:</p>
<ol type="1">
<li><p>Native Geneve network inside ZGC for Network Func Chains (Benefit of TLV extensibility &amp; HW support), Mizar DP is like extend FWD into compute node, consistent with this, shouldn’t go backwards</p></li>
<li><p>Configurable overlay modes (VxLAN-GPE or Geneve) for Tenant network</p></li>
</ol></td>
</tr>
<tr class="even">
<td></td>
<td></td>
<td></td>
<td></td>
</tr>
</tbody>
</table>

<span id="_Toc396111629" class="anchor"></span>Appendix C: Glossary

Instructions: Provide clear and concise definitions for terms used in
this document that may be unfamiliar to readers of the document. Terms
are to be listed in alphabetical order.

<span id="_Ref441754492" class="anchor"></span>Table 6 - Glossary

|          |             |                |
| -------- | ----------- | -------------- |
| Term     | Acronym     | Definition     |
| \<Term\> | \<Acronym\> | \<Definition\> |
| \<Term\> | \<Acronym\> | \<Definition\> |
| \<Term\> | \<Acronym\> | \<Definition\> |

## Appendix B: Glossary ##

<span id="_Toc396111630" class="anchor"></span>

## Appendix C: Referenced Documents ##

\[1\] Sherif, Phu and Cathy [***Zeta: Modular Network Services via
Distributed and Elastic Middleboxes***](https://github.com/futurewei-cloud/mizar/pull/176)

\[2\] ***Mizar project official documentation:***[<span class="underline">https://mizar.readthedocs.io/en/latest/</span>](https://mizar.readthedocs.io/en/latest/)

<span id="_Toc396111631" class="anchor"></span>

## Appendix D: Review Comments ##

This is a live document and will continue evolving as we progress. This
session will capture important review and discussion outputs for the
benefit of open community to understand the historical contexts,
regarding some of the design and decisions make during the journey.

<span id="_Toc398804287" class="anchor"></span>Table 7 – Review Comments

| Comments | Date |
| -------- | ---- |
|          |      |
|          |      |
|          |      |
|          |      |


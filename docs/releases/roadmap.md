# Scenarios

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

# RoadMap

## Release 0.1 (09/30/2019) (Done)

This release includes:

 *  A basic implementation of data plane and a mini controller;
 *  Create and deletion of VPC/subnet/ports objects.
 *  Initial automated test and deployment scripts.

## Release 0.5 (12/30/2019)

This release continues to build features for scenario #1 while support scenario #2:

* Performance improvement.
* CNI plugin for Mizar.
* Other integration work with Kubernetes.
* Neutron plugin for Mizar. 
* Scaled endpoint.

## Release 0.7 (04/30/2020)

This release continues to build features for scenario #1 and #2, and adds support for scenario #3:

* Network policy support for Kubernetes.
* Fast Path.
* Security group.
* Network ACL.
* Routing Table and Inter-VPC routing.

## Release 1.0 (08/30/2020)

This release marks a relatively-complete experience for scenarios #1-#4. But lots of X features or integration work may still not be done, like integration with SNAT/DNAT, LBs, floating IPs, etc.

* Auto-scale transit switches and transit routes.
* Hardware offloading.
* Monitoring and telemetry.
* Live migration and live update.
* Improved deployment and configuration experience.
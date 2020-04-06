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

### Summary

This release introduces a new management plane for Mizar, designed and
developed from the ground up. The design relies on extensibility
features in Kubernetes including Custom Resource Definitions and
Operators. Mizar Management Plane has several objectives:

1. Replace Kubeproxy with the scaled endpoint
1. Improve Mizar usability and deployability
1. Improve Mizar control-plane and data-plane Interfacing and workflow
1. Facilitate end-to-end testing, validation, and performance
   benchmarks
1. Extensibility to support other data-plane technologies, including ebpf, OVS, and host-networking.

### Breaking Changes

This release does not involve breaking changes to existing
integrations.

### Data Plane

* Update kernel requirement to 5.6-rc2
* Minor Unit test fix [bdfc1f9](https://github.com/futurewei-cloud/mizar/commit/bd9037c1482c787dbcb7529085003830213b848a)
* Direct path for cross network traffic [b5283a1](https://github.com/futurewei-cloud/mizar/commit/f2b6b07445903a263a86a600ccf29e5cc8010ef0)

### Mizar Management plane

* Mizar objects with [Custom Resource Defintions](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
* VPC, Net, Endpoint, Bouncer, Divider and Operators, Main
    Commits:
    [644d0fa](https://github.com/futurewei-cloud/mizar/commit/96fb43913b47266339fe162343f868a438085abe),
    [21a43c3](https://github.com/futurewei-cloud/mizar/commit/8934e2685ed38745a448012ad4d0653ab6027c9f),
    [8934e26](https://github.com/futurewei-cloud/mizar/commit/84f47d0b1e4fb045feff777661cb589060f18dfd)
* Built-in Operators for K8s Pods and Services, Main
    Commits: [42abe77](https://github.com/futurewei-cloud/mizar/commit/330e2ebe2993bf4e853c1defa22fe6d4994a752e)
* Basic Bouncer and Divider Placement, Main
    Commits:
    [f12eb3b](https://github.com/futurewei-cloud/mizar/commit/fda477df4f327366cede6c58aa64c9a498207865)
* Simple manual scaling workflows for bouncers and dividers, Main
    Commits:
    [5b7c325](https://github.com/futurewei-cloud/mizar/commit/42abe77493ce6c6421ccb4589c3b5ae31fd7f15f),
    [354dda1](https://github.com/futurewei-cloud/mizar/commit/5b7c3255653b80093b2ab4a4fa3ef58685c93ac0)

* Replaces KubeProxy for Loadbalancer type with scaled-endpoint, Main
      Commits:
   [42abe77](https://github.com/futurewei-cloud/mizar/commit/330e2ebe2993bf4e853c1defa22fe6d4994a752e)
* Generic CNI RPC Interface for transit daemon, Main
      Commits: [ffa7e6a](https://github.com/futurewei-cloud/mizar/commit/70b992b44b591ad14eb1d94810235b811cda9a4c)
* Endpoint host management with Netlink, Main
      Commits: [5b46462](https://github.com/futurewei-cloud/mizar/commit/b347e23ec119512e344697b3e2e46f34f17378ec)

### Documentation

* New [documentation readthedocs page](http://mizar.readthedocs.io)
    * Detailed data-plane design
    * Detailed management-plane design
    * Improvement in getting started guide to using the new management plane

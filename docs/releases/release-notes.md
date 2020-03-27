## Release 0.1 (09/30/2019)

 *  A basic implementation of data plane and a mini controller;
 *  Create and deletion of VPC/subnet/ports objects.
 *  Initial automated test and deployment scripts.

## Release 0.5 (12/30/2019)

 * Fast path (beta)
 * Scaled endpoint (beta)
 * Components name changes
 * Performance improvements
 * Extensible packet processing pipeline support
 * Codedeploy support

## Release 0.7 (03/30/2020)

### Summary

This release introduces a new management plane for Mizar, designed and
developed from the ground up. The design relies on extensibility
features in Kubernetes in cluding Custom Resource Definitions and
Operators. The Management Plane is built with several objectives in
mind:
1. Replace Kubeproxy with the scaled endpoint
1. Improve Mizar usability and deployability
1. Improve Mizar control-plane and data-plane Interfacing and workflow
1. Facilitate end-to-end testing, validation, and performance
   benchmarks
1. Extensibility to support other data-plane technologies including
   ebpf, OVS, and host-networking.

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
    * Improvement in getting started guide to use the new management plane



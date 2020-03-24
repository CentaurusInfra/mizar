## Release 0.1 (09/30/2019)

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
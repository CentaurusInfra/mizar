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
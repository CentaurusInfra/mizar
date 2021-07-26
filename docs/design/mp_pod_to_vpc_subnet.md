<!--
SPDX-License-Identifier: MIT
Copyright (c) 2021 The Authors.

Authors: Phu Tran          <@phudtran>

-->

# Mizar User defined VPCs and Subnets for Vanilla Kubernetes

## Introduction

This document defines the interface for users to define their own VPCs and subnets. Furthermore, it also describes the interface for assigning pods to these specific subnets and VPCs.

## Custom VPC Creation

When creating a VPC, users must define the VPC's name, IP, prefix, and the number of dividers.

An example is given below.

```yaml
apiVersion: "mizar.com/v1"
kind: Vpc
metadata:
  name: vpc0
spec:
  ip: "12.0.0.0"
  prefix: "8"
  dividers: 2
```

#### Requirements
- The CIDR range is valid.
- The VPC must not already exist.

## Custom Subnet Creation

When creating a subnet users must define the subnet's name, IP, prefix  the number of bouncers, and the VPC that it belongs to.

An example is given below.

```yaml
apiVersion: "mizar.com/v1"
kind: Subnet
metadata:
  name: net0
spec:
  vpc: "vpc1"
  ip: "12.2.0.0"
  prefix: "16"
  bouncers: 2
```
#### Requirements
- The CIDR range the subnet is given must be within the range of the parent VPC's range.
- The Parent VPC must exist.
- The new subnet must not yet already exist within the VPC.

## Pod to VPC and Subnet designation

Three options are defined for assigning pods to specific VPCs.

### Placing a pod into the default VPC

Creating a standard pod with no Mizar specific annotation will assign it to the default VPC that is created at Mizar setup.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
      - containerPort: 443
```

### Placing a pod into a specific VPC

Users can place a pod into a specific VPC by specifying the VPC annotation like below.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  annotations:
    mizar.com: {"vpc": "vpc0"}
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
      - containerPort: 443
```

#### Requirements
- The Parent VPC must exist.
- The VPC must have an existing subnet.

The pod is invalid if the VPC does not exist.

### Placing a pod into a specific VPC and Subnet

Users can place a pod into a specific VPC and subnet by specifying the required VPC and subnet annotation like below.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  annotations:
    mizar.com: {"vpc": "vpc0", "subnet": "subnet0"}
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
      - containerPort: 443
```
The pod definition is invalid if the VPC or subnet does not exist.

#### Requirements
- The Parent VPC must exist.
- Within the parent VPC must exist the specified subnet.
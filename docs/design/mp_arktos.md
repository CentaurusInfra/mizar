<!--
SPDX-License-Identifier: MIT
Copyright (c) 2020 The Authors.

Authors: Catherine Lu      <@clu2>

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

# Arktos Network and Mizar Integration

## Introduction

This document is designated for Arktos service using Mizar as its underline network system. In this document, you will find the design detail on how to integration Arktos multi-tenancy network object with Mizar as its network platform, so that Arktos can fully utilize network objects offered in Mizar, including vpcs, nets, services, pods, bouncers and dividers. 

## Arktos Network Object Overview: 
The Arktos network object contains its type and type-specific configurations, which translates into spec fields type and vpcID:
```yaml
apiVersion: arktos.futurewei.com/v1
kind: Network
metadata:
  name: vpc-1
spec:
  type: mizar
  vpcID: vpc-1a2b3c4d
```
The type field is the only required field, where it identifies the underline network service (which in our case is mizar). VpcID field is optional, and it lists the vpc id that is associated with this Arktos network object. If vpcID is not specified, the default VPC will be used. 

Below is the definition of a flat network, where the defaul network is used: 
```yaml
apiVersion: arktos.futurewei.com/v1
kind: Network
metadata:
  name: default
spec:
  type: flat
```

The Arktos network object and VPC have **many to one relationship**, where multiple Arktos network objects can reference the same VPC network. 

## Pod Definition
When a pod is attached to the default network, nothing is needed in pod spec:

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

When a pod is attached to a certain network, it needs to set its "network" in labels:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    arktos.futurewei.com/network: vpc-1
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
      - containerPort: 443
```

When a pod is attached to a certain network, then it needs to specify subnet or IP. It can be expressed in annotations:

```yaml

apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    arktos.futurewei.com/network: vpc-1
  annotations:
    arktos.futurewei.com/nic: {"name": "eth0", "ip": "10.10.1.12", "subnet": "net1"}
    arktos.futurewei.com/vip-hint: {"cidr":"10.10.1.0/26", "ip":"10.10.1.12", "policy":"BestEffort"}
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
      - containerPort: 443

```

Annotation ```arktos.futurewei.com/nic``` is for user to provide optional information about pod nic. The recognized keys of element include:

|key|exemplary value|
|---:|---:|
|name|eth0|
|subnet|subnet-1, or 192.168.100.0/26|
|ip|192.168.100.5|

Please note that any of the three fields can be missing. For example, user might only specify  ```ip``` field; in this case, Mizar needs to figure out which subnet this ip falls into, and creates the pod into the correct subnet. 

## Network Object Association

In Mizar, the association of all network objects are stored as key/value sets in Mizar’s object store. For instance, 

The Arktos network object is associated with Mizar vpc as: 
	```self.store.vpcs_arktosnet_store[arktosnet.name] = {}```
    ```self.store.vpcs_arktosnet_store[arktosnet.name][vpc.name] = vpc_object```

The Arktos network object is associated with services in similar ways: 
    ```self.store.services_arktosnet_store[arktosnet.name] = {}```
    ```self.store.services_arktosnet_store[arktosnet.name][service.name] = service_object```

In addition, Mizar already provides key/value sets to store relationships between endpoints/pods, subnets/nets and vpcs: 

* ```nets_vpc_store```
* ```eps_net_store```

## Arktos Network Object Creation 

For now, Mizar will only support VPC object and Arktos network object association, meaning Arktos must pass in a vpc id that already exist. 

Mizar has operator that is in charge of managing lifecycle of Arktos network object. 

In case of flat network: 
```yaml
apiVersion: arktos.futurewei.com/v1
kind: Network
metadata:
  name: default
spec:
  type: flat
```
Operator kicks off Arktos network object ```default``` creation process, and then associated with the default network ```vpc0``` in Mizar:
```self.store.vpcs_arktosnet_store[default][vpc0] = vpc0 object```

In case of vpc network: 
```yaml
apiVersion: arktos.futurewei.com/v1
kind: Network
metadata:
  name: vpc-1
spec:
  type: mizar
  vpcID: vpc-1a2b3c4d
```
Operator starts creation process for Arktos network object ```vpc-1```, and then search for existing vpc object in Mizar to find vpc with id = vpc-1a2b3c4d. Once the vpc object is found, it then associated with the newly created Arktos network object ```vpc-1```: 
    ```self.store.vpcs_arktosnet_store[vpc-1][vpc-1a2b3c4d] = vpc-1a2b3c4d object```

## Pod Creation
 Sample Pod definition:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
  labels:
    arktos.futurewei.com/network: vpc-1
  annotations:
    arktos.futurewei.com/nic: {"name": "eth0", "ip": "10.10.1.12", "subnet": "net1"}
    arktos.futurewei.com/vip-hint: {"cidr":"10.10.1.0/26", "ip":"10.10.1.12", "policy":"BestEffort"}
spec:
  containers:
  - name: nginx
    image: nginx
    ports:
      - containerPort: 443
```
Operator kicks off creation process:
* List Kubernetes cluster object / Arktos newtork object
* Retrieve ```labels``` and ```annotations``` information: 
    * ```arktos.futurewei.com/network```: vpc-1
    * ```arktos.futurewei.com/nic```: {"name": "eth0", "ip": "10.10.1.12", "subnet": "net1"}
* Find Arktos network object that is listed in ```arktos.futurewei.com/network```
* Find subnet and ip information from ```arktos.futurewei.com/nic```, and choose the correct subnet to place the new pod. 
* If neither IP nor subnet is specified, Mizar will pick the first subnet within ```vpc-1``` and assign pod to that subnet.
* Update object store: map subnet object (which is equivalent to net object in Mizar) with pod: ```self.store.eps_net_store[net1][nginx] = pod object```
* After Pod creation is completed, update Pod object with new annotations: ```arktos.futurewei.com/network_user_input``` and ```arktos.futurewei.com/network-readiness```.      
* ```arktos.futurewei.com/network_user_input``` will include Mizar network information such as ```vpc name```, ```subnet name``` and ```ip address```
* Once Pod is provisioned, operator will set ```arktos.futurewei.com/network-readiness == true```. 

* In return, the annotations becomes: 
```yaml
  annotations:
    arktos.futurewei.com/nic: {"name": "eth0", "ip": "10.10.1.12", "subnet": "net1"}
    arktos.futurewei.com/vip-hint: {"cidr":"10.10.1.0/26", "ip":"10.10.1.12", "policy":"BestEffort"}
    arktos.futurewei.com/network-readiness: "true"
    arktos.futurewei.com/network_user_input: {"vpc": "vpc-1", "net": "net1", "ip": "10.10.1.12"}
```
Note: Integrity checks are needed here, where we need make sure that the ip address falls within subnet CIDR range and service CIDR range, and subnet CIDR range falls within the VPC's (vpc-1) CIDR range.


### Service Creation 

* List Kubernetes cluster object / Arktos newtork object
* In case of using services, vpcID should not listed, and default network is selected
* Waiting on customer to create service using yaml file:  
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  network: my-network
  selector:
    app: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```
* Create ```my-service```
* Update object store: map Arktos network with services: ```self.store.services_arktosnet_store[my-network][my-service] = service_object```
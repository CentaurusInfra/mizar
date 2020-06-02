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
spec:
  type: mizar
  vpcID: vpc-1a2b3c4d
```
The type field is the only required field, where it identifies the underline network service (which in our case is mizar). VpcID field is optional, and it lists the vpc id that is associated with this Arktos network object. If vpcID is not specified, the default VPC will be used. 

The Arktos network object and VPC have **one to one relationship**, where one Arktos network object only targets to one VPC in Mizar. In other words, Arktos network object is equivalent to a vpc object in Mizar. 

## Mizar VPC Object Overview: 
In Mizar, VPC object has two required fields: ip and prefix, where in combination, they compose the CIDR of the VPC. For example, for CIDR 10.0.0.0/16, the ip = 10.0.0.0 and prefix = 16. 
```yaml
spec:
  ip: 10.0.0.0
  prefix: 16
```
## Proposal 
Given the fact that Arktos network object is equivalent to vpc object in Mizar, I would like to propose two options: 

### OPTION ONE: 
Arktos adds two more optional fields into its spec, ip and prefix. This will address situations where the custom vpcID listed in Arktos network object has not been created, and Mizar needs to know the CIDR range in order to create a VPC object. The spec should show something like this: 
```yaml
spec:
  type: mizar
  vpcID: vpc-1a2b3c4d
  ip: 10.0.0.0
  prefix: 16
```
When new VPC is created and mapped with Arktos network object, the data is stored as a key/value pair in Mizar’s object store, ```self.store.vpcs_arktosnet_store[arktosnet.name][vpc.name] = vpc_object```

### OPTION TWO: 
Arktos can directly use Mizar’s VPC CRD to define its network object. As mentioned in Arktos network object overview section, Arktos network object is equivalent to VPC object in Mizar. Thus, Arktos can adapt Mizar’s VPC CRD to define Arktos network object: 
```yaml
apiVersion: mizar.com/v1
kind: Vpc
metadata:
  name: vpc0
spec:
  ip: 10.0.0.0
  prefix: 16
  status: Init
  dividers: 2
```
where status is always “Init” when creating a new VPC object, and dividers specifies the number of dividers/subnets desired. The ip and prefix fields as mentioned previous, together they define the CIDR range of the VPC.

### Network Object Association

In both options, the association of all network objects are stored as key/value sets in Mizar’s object store. For instance, 

The Arktos network object is associated with Mizar vpc as: 
	```self.store.vpcs_arktosnet_store[arktosnet.name] = {}```
    ```self.store.vpcs_arktosnet_store[arktosnet.name][vpc.name] = vpc_object```

The Arktos network object is associated with services in similar ways: 
    ```self.store.services_arktosnet_store[arktosnet.name] = {}```
    ```self.store.services_arktosnet_store[arktosnet.name][service.name] = service_object```

In addition, Mizar already provides key/value sets to store relationships between endpoints/pods, subnets/nets and vpcs: 

* ```nets_vpc_store```
* ```eps_net_store```

## Analysis
The following describes in detail on the steps involved during creation of each network object such as services and vpcs. 

### The Arktos network object is associated with a vpcID that already exists:
```yaml
spec:
  type: mizar
  vpcID: vpc01
  ip: 10.0.0.0
  prefix: 16
  subnets:
  -  net1
  -  net2
```
* List Kubernetes cluster object / Arktos newtork object
* Find vpc object that is associated with the vpcID
* Update object stores: map Arktos network with vpc id and stored as a key/value pair. 
* If subnet objects (which is equivalent to nets in Mizar language) are also listed, Mizar has object store to specify net objects to vpc object association: ```self.nets_vpc_store[net.vpc][net.name] = net_object``` Thus, the net objects can be linked with arktos network object through ```nets_vpc_store``` and ```vpcs_arktosnet_store``` (mentioned in proposal section)

### The Arktos network object is associated with a vpcID that does not exist yet: 
```yaml
spec:
  type: mizar
  vpcID: vpc123f3
  ip: 172.0.0.0
  prefix: 16
```
* List Kubernetes cluster object / Arktos newtork object
* If not able to find vpc object with specified vpcID, trigger VPC creation workflow to create a new VPC with listed CIDR range. 
* The following steps are the same as previous section. 

### The Arktos network object is associated with multiple services and the default network is used:
```yaml
spec:
  type: mizar
```
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

###	Pod creation 
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
  network: vpc-1
  nics:
    - subnet: subnet-1
      ip: 192.168.0.12
```
* Create pod (equivalent to ```endpoint``` in Mizar) named ```nginx``` 
* Update object store: map subnet object (which is equivalent to net object in Mizar) with pod: ```self.store.eps_net_store[subnet-1][nginx] = pod_object```
Note: Integrity checks are needed here, where we need make sure that the ip address falls within subnet CIDR range, and subnet CIDR range falls within the VPC's (vpc-1) CIDR range.
* If neither IP or subnet is specified, Mizar will pick the first subnet within ```vpc-1``` and assign pod to that subnet.
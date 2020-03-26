We categorize network objects and operators as generic, and data-plane
specific. Generic network object primarily extends [Kubernetes Network
Model](https://kubernetes.io/docs/concepts/cluster-administration/networking/#the-kubernetes-network-model). Data-plane
specific network objects are specific to the underlying data-plane
requirements. For example, in Mizar we have the abstract concpets of Bouncers
and Dividers, hence we have speific objects and operators for them.

### Generic Objects


#### **Droplet Operator**:

#### **VPC Operator**:

#### **Network Operator**:

#### **Endpoint Operator**:

As we extend Mizar's features, we will be introducing more operators
such as: security group operator, nacl.

### Data-plane Specific Objects

In case of Mizar, we have two unique objects that the management plane
manages its life-cyle: Bouncers and Dividers. For these objects, we have
introduced the following operators:

#### **Bouncer Operator**:
#### **Divider Operator**:
We categorize network objects and operators as generic, and data-plane
specific. Generic network object primarily extends [Kubernetes Network
Model](https://kubernetes.io/docs/concepts/cluster-administration/networking/#the-kubernetes-network-model). Data-plane
specific network objects are specific to the underlying data-plane
requirements. For example, in Mizar we have the abstract concpets of Bouncers
and Dividers, hence we have speific objects and operators for them.

All objects are defined through Kubernetes CRDs under the `mizar.com`
resource group. An operator exposes interfaces to the management-plane
workflows. The interface acts on any object if the action requires
data from the operator's stateful object. For example the droplet
operator provide interfaces to place a divider or bouncer given that
it has complete information about the states of droplets (its own
stateful object).

The operators interfaces by themselves do not carry any weight until
invoked by a [workflows](md_workflows.md).

### Generic Objects

The current generic objects managed by Mizar are: 1) Droplet, 2) VPC, 3) Network,
4) Endpoint. As we extend Mizar's features, we will be introducing more operators
such as: Security Groups, NACLs.

#### **Droplet Operator**:

Droplets refer to a physical interface on a host where the Transit XDP
program is running. The following CRD spec defines a droplet:

```yaml
    - name: Mac
      type: string
      priority: 0
      JSONPath: .spec.mac
      description: The mac address of the endpoint
    - name: Ip
      type: string
      priority: 0
      JSONPath: .spec.ip
      description: The IP of the endpoint
    - name: Status
      type: string
      priority: 0
      JSONPath: .spec.status
      description: The Current Status of the droplet
    - name: Interface
      type: string
      priority: 0
      JSONPath: .spec.itf
      description: The main interface of the droplet
```

The droplet operator exposes the following interfaces:

1. Track droplets health and performance metrics
1. Placement of bouncers (Mizar DP only)
1. Placement of dividers (Mizar DP only)

#### **VPC Operator**:

The following CRD spec defines a VPC:

```yaml
    - name: Ip
      type: string
      priority: 0
      JSONPath: .spec.ip
      description: The IP of the VPC CIDR block
    - name: Prefix
      type: string
      priority: 0
      JSONPath: .spec.prefix
      description: The prefix of the VPC CIDR block
    - name: Vni
      type: string
      priority: 0
      JSONPath: .spec.vni
      description: The VNI of the VPC
    - name: Dividers
      type: integer
      priority: 0
      JSONPath: .spec.dividers
      description: The number of dividers of the VPC
    - name: Status
      type: string
      priority: 0
      JSONPath: .spec.status
      description: The Current Provisioning Status of the net
```

The vpc operator exposes the following interfaces:

1. Create/delete a default VPC (for single-Tenant Kubernetes and for
   substrate endpoints)
1. Allocate the VPC's VNI
1. Initial creation of dividers (Mizar DP only)
1. Elastic scaling of dividers (Mizar DP only)

#### **Network Operator**:

The following CRD spec defines a Network:

```yaml
    - name: Ip
      type: string
      priority: 0
      JSONPath: .spec.ip
      description: The IP of the NET CIDR block
    - name: Prefix
      type: string
      priority: 0
      JSONPath: .spec.prefix
      description: The prefix of the NET CIDR block
    - name: Vni
      type: string
      priority: 0
      JSONPath: .spec.vni
      description: The VNI of the VPC
    - name: Vpc
      type: string
      priority: 0
      JSONPath: .spec.vpc
      description: The name of the VPC
    - name: Status
      type: string
      priority: 0
      JSONPath: .spec.status
      description: The Current Provisioning Status of the net
    - name: Bouncers
      type: integer
      priority: 0
      JSONPath: .spec.bouncers
      description: The number of bouncers of the Net
```

The network operator exposes the following interfaces:

1. Create/delete a default Network (for single-Tenant Kubernetes and for
   substrate endpoints)
1. Allocate/Deallocate endpoints' IP addresses
1. Initial creation of bouncers (Mizar DP only)
1. Elastic scaling of bouncers (Mizar DP only)
1. Initialize simple endpoint's Transit Agent (Mizar DP only)

#### **Endpoint Operator**:

The following CRD spec defines an Endpoint:

```yaml
   - name: Type
      type: string
      priority: 0
      JSONPath: .spec.type
      description: The type of the endpoint
    - name: Mac
      type: string
      priority: 0
      JSONPath: .spec.mac
      description: The mac address of the endpoint
    - name: Ip
      type: string
      priority: 0
      JSONPath: .spec.ip
      description: The IP of the endpoint
    - name: Gw
      type: string
      priority: 0
      JSONPath: .spec.gw
      description: The GW of the endpoint
    - name: Prefix
      type: string
      priority: 0
      JSONPath: .spec.prefix
      description: The network prefix of the endpoint
    - name: Status
      type: string
      priority: 0
      JSONPath: .spec.status
      description: The Current Provisioning Status of the endpoint
    - name: Network
      type: string
      priority: 0
      JSONPath: .spec.net
      description: The network of the endpoint
    - name: Vpc
      type: string
      priority: 0
      JSONPath: .spec.vpc
      description: The vpc of the endpoint
    - name: Vni
      type: string
      priority: 0
      JSONPath: .spec.vni
      description: The VNI of the VPC
    - name: Droplet
      type: string
      priority: 0
      JSONPath: .spec.droplet
      description: The droplet hosting the endpoint
    - name: Interface
      type: string
      priority: 0
      JSONPath: .spec.itf
      description: The interface name of the endpoint
    - name: Veth
      type: string
      priority: 0
      JSONPath: .spec.veth
      description: The veth peer interface name of the endpoint
    - name: Netns
      type: string
      priority: 0
      JSONPath: .spec.netns
      description: The netns of the endpoint
    - name: HostIp
      type: string
      priority: 0
      JSONPath: .spec.hostip
      description: The Host IP of the endpoint
    - name: HostMac
      type: string
      priority: 0
      JSONPath: .spec.hostmac
      description: The Host MAC of the endpoint
```

The endpoint operator exposes the following interfaces:

1. Update bouncers with endpoints information - e.g. add or delete an
   endpoint (Mizar DP only)
1. Update endpoints when a bouncer is added or deleted (Mizar DP only)
1. Create scaled endpoints(Mizar DP only)
1. Update scaled endpoints remote IPs (Mizar DP only)

### Data-plane Specific Objects

In case of Mizar, we have two unique objects that the management plane
manages its life-cyle: Bouncers and Dividers. For these objects, we have
introduced the following operators:

#### **Bouncer Operator**:

The following CRD spec defines a Bouncer:

```yaml
    - name: vpc
      type: string
      priority: 0
      JSONPath: .spec.vpc
      description: The VPC of the divider
    - name: net
      type: string
      priority: 0
      JSONPath: .spec.net
      description: The Network of the bouncer
    - name: Ip
      type: string
      priority: 0
      JSONPath: .spec.ip
      description: The IP of the droplet
    - name: Mac
      type: string
      priority: 0
      JSONPath: .spec.mac
      description: The mac address of the divider's droplet
    - name: Droplet
      type: string
      priority: 0
      JSONPath: .spec.droplet
      description: The name of the droplet resource
    - name: Status
      type: string
      priority: 0
      JSONPath: .spec.status
      description: The Current Status of the divider
```

The bouncer operator exposes the following interfaces:

1. Update bouncers of a network when a divider is added or deleted
1. Update bouncers with endpoints when a bouncer is added or deleted

#### **Divider Operator**:

The following CRD spec defines a Divider:

```yaml
    - name: vpc
      type: string
      priority: 0
      JSONPath: .spec.vpc
      description: The VPC of the divider
    - name: Ip
      type: string
      priority: 0
      JSONPath: .spec.ip
      description: The IP of the divider's droplet
    - name: Mac
      type: string
      priority: 0
      JSONPath: .spec.mac
      description: The mac address of the divider's droplet
    - name: Droplet
      type: string
      priority: 0
      JSONPath: .spec.droplet
      description: The name of the droplet resource
    - name: Status
      type: string
      priority: 0
      JSONPath: .spec.status
      description: The Current Status of the divider
```

The divider operator exposes the following interfaces:

1. Update dividers when a bouncer is created/deleted
1. Update dividers when a network is created/deleted
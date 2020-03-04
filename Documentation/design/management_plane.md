
# Mizar Management Plane

## Overall Architecture

![Overall Architecture](./figures/management_plane.png)

### Generic Operators

* **Droplet Operator**:
* **VPC Operator**:
* **Network Operator**:
* **Endpoint Operator**:

As we extend Mizar's features, we will be introducing more operators
such as: security group operator, nacl.

### Mizar specific operators
* **Bouncer Operator**:
* **Divider Operator**:


### Object-Pipeline Pattern

![Object pipeline](./figures/object_pipeline.png)

### Resumable Object Processing

### Horizontal Scaling

### Stateful Operator Resilience

## Workflows

### VPC Object Life Cycle

### Network Object Life Cycle

### Endpoint Object Life Cycle

### Divider Object Life Cycle (Mizar Specific)

### Bouncer Object Life Cycle (Mizar Specific)

### Compatability of other Data-planes (OVS)

This architecture is extensible to derive other data-plane systems and
is compatible with existing cloud networking solutions (particularly
neutron). For example, if we would like to introduce a L2 ovs that is
responsible for managing a network overlay, we shall introduce a new
object (e.g. L2Agent), and a new operator (L2Operator). The L2Agent
object will have multiple states to provision OVS on each host. The
L2Operator will be responsible for mutating the state of existing
objects using its knowledge about the current state of an OVS switch
on the host and the requriment of the mutated object and also program
OVS through direct RPC interface exposed by the transitd. For example
when an endpoint is provisioned the Network operator mutate the
endpoint object with a list of all the hosts of the network and move
the endpoint object to L2-Agent-Ready state. The L2Agent operator
watches for endpoints in this state, and program all the OVS in the
relevant hosts with the appropriate flow-rules to ensure connectivity.
The data-plane supports an internal protocol to facilitate data-plane
programming through remote RPC. Any management plane that would incorporate
Mizar's data-plane shall use these programming interface. [Mizar
management-plane](mp_overview.md) provides a detailed workflows.

Fundamentally, users perform nine operations that shall be supported by the
management-plane workflow:

- Create/Update/Delete VPC
- Create/Update/Delete Network
- Create/Update/Delete Endpoint

The workflows for a create/update/delete  API are similar (not necessarily
exact). For simplicity of presentation, I will focus on the creative workflow
to illustrate the requirements  of the control-plane business logic.

Conceptually -  and in high level  - there are three lookup tables in each
transit XDP program.

- **VPC table**: A  key/value table where the key is the tunnel id of the VPC,
  and the value is the list of the dividers of the VPC.
- **Network table**: A key/value table where the key is the network ip, and the
  value is the list of the bouncers of the VPC.
- **Endpoint table** A key/value table where the key is the endpoint IP, and the
  value is the host of the endpoint.

Note: See the  trn_datamodel.h file for the exact definition of the table keys
and data values.

#### Create VPC

On creating a VPC, the control-plane workflow shall be as follows:

1. Trigger the placement algorithm to allocate multiple dividers to the  VPC.
   For example, VPC0->[R1, R2], where R1  and R2 are the IP addresses of the
   substrate node (host) functioning as a divider.
1. Call an update_vpc API  on  R1  and  R2  that populates their VPC table. For
   example, the  VPC table in  both R1 and  R2 shall  have the following
   information:

| Tunnel ID | VPC      |
|-----------|----------|
| VPC0      | [R1, R2] |

Table: VPC table in R1 and R2

### Create Network

When the  user creates a  network within a  VPC, for example, net0 and net1 in
vpc0 (where net0 and  net1 are the network  addresses of net0 and net1), the
control-plane workflow shall be as follows:

1. Trigger the placement algorithm to allocate multiple bouncers for net0 and
   net1. For  example net0 -> [S00, S01], where S00 And S01 are the IP addresses
   of the bouncers serving net0. Similarly,  net1 ->  [S10, S11],  where S10 and
   S11 are the IP addresses of the bouncers serving net1.

1. Call an update_net  API first on the R1 and  R2 that populates their Network
   table.  In our example, the network table  of R1 and  R2 shall look like:

| Network Key  | Network    |
|--------------|------------|
| {net0, VPC0} | [S00, S01] |
| {net1, VPC0} | [S10, S11] |

Table: Network table in R1 and R2

1. Call an update_vpc API for the bouncers of net0 and the bouncers of net1.
   Accordingly, the VPC tables in S00, S01, S10, S11 shall look like:

| Tunnel ID | VPC      |
|-----------|----------|
| VPC0      | [R1, R2] |

Table: VPC table in S00, S01, S10, S11

### Create endpoint

When the  user ** attaches** an endpoint  to a container, the  control plane
needs to perform four main actions (through the data-plane):

1. Create the actual virtual interface on the host
2. Execute the transit agent xdp  program  on  the  virtual interface
3. Populate  the  endpoint metadata on the  transit agent xdp program
4. Populate the endpoint table on all the bouncers of the network with routing
   entries of the new endpoint.

Let's consider; for example, the user attaches a simple endpoint ep0 in net0 to
a VM in host0. ep0  is the virtual IP of the endpoint, and host0 is the IP
address of the host. The control-plane workflow shall be as follows:

1.  Call a create_endpoint  API  for  host0. Accordingly, the network
    control-plane agent shall create a virtual interface pair  veth0 ->
    veth0_root,  attach veth0 to the compute resources (e.g., container
    namespace), and load the transit agent program on veth0_root.

1.  Call an update_network  API  for the transit agent Running on veth0_root.
    The network table on the transit agent shall look like

| Network Key  | Network    |
|--------------|------------|
| {net0, VPC0} | [S00, S01] |

Table: Network table of Transit agent of veth0_root

1.   Call an  update_endpoint API  for net0 bouncers;  S00 and S01. Accordingly,
     the network table on net0 bouncers shall look like:

| Endpoint Key | Endpoint |
|--------------|----------|
| {VPC0, ep0}  | [host0]  |

Table: Endpoint table of S00 and S01

### Summary of Workflows

The following table summarizes the primary control-plane workflows as well as
the table to be populated during each operation.

| User API/Events | Control-Plane Algorithm                                                    | Data-plane RPCs                                                                                                                                      | Data-plane ebpf map                                                         |
|-----------------|----------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Create VPC      | Allocate dividers for the VPC                                       | call update_network on all dividers of the VPC (optional)                                                                                         | Populate VPC map (transit XDP program)                                     |
| Create Network  | Allocate bouncers for the network                                  | 1) Call,update_vpc on all bouncers of the network,2) Call,update_network on all bouncers (optional)                                 | Populate VPC map (transit XDP program)                                      |
| Attach Endpoint | Invoke virtual interface creation procedures (e.g., netns, libvert) on host | 1) Call create_endpoint on host, 2) Call update_network on transit, agent of the host, 3) Call update_endpoint on all bouncers of,the network | Populate, Endpoint map,(transit XDP,program), Network map (of,transit agent) |
| Update VPC      | Update the vpc data                                                        | 1) Call,update_vpc on,all bouncers,of networks,inside the,VPC, 2) Call update_vpc in dividers in the VPC (optional)                   | Populate VPC map (transit XDP program)                                      |
| Update Network  | Update network data in all endpoint's transit agents                       | Call update_network in all endpoints of a network                                                                                                    | Populate Network map of transit agent                                       |
| Update Endpoint | Update endpoint data in bouncers of the network                    | Call update_network in all the bouncers of an endpoint                                                                                       | Populate Endpoint map (transit XDP program)                                 |
| Delete VPC      | (Applicable only if VPC has no network)                                    | 1) Call,delete_vpc on all, bouncers ,of all networks,in the,VPC, 2) Call delete_vpc on all dividers in the VPC (optional)               | Populate VPC map (transit XDP program)                                      |
| Delete Network  | Applicable only if a network has no endpoints                                | 1) Call,delete_network on all, dividers, of the VPC,2) Call,delete_network on bouncers of the network (optional)                       | Populate Network map (transit XDP program)                                  |
| Delete Endpoint | Deletes the endpoint and unload the transit agent program on the host      | 1) Call delete_endpoint, on all, bouncers, of a network, 2) Unload the transit agent xdp program on the peer virtual interface.                 | Populate Endpoint map (transit XDP program)                                 |

Table: Summary of workflows

## Smart Decisions and Monitoring Considerations

Mizar provides a simple, efficient, and flexible mechanisms to create overlay
networks with various types of endpoints support at scale.  The management-plane
continuously optimizes the placement of the bouncers and dividers.

Smart Scaling and Placement algorithms are at  the primary mechanisms to
achieve  smart decisions, including:

- Smart Routing
- Smart Configuration
- Smart Congestion control

Placement and  Scaling entail determining which transit xdp program (physical
host) shall be configured to function as a bouncer or divider.

Placement objectives of  bouncers and dividers can  be, but not limited to:

**Accelerate Endpoint Provisioning**: For example, in serverless applications,
endpoint provisioning is very frequent. Thus the placement algorithm shall
minimize the number of bouncer to be used within a network while ensuring that
the bouncers are placed on nodes of sufficient bandwidth to accommodate the
applications traffic.

**Minimize Communication Latency**: For example in applications where VPC
configuration is not frequently changed or for latency-sensitive applications
(e.g., conventional IT  applications, predefined compute clusters), the
placement algorithm shall minimize latency by ensuring that the bouncers placed
in proximity or co-location with endpoints.

**Improve Network Resiliency**: Typically bouncers shall be placed within the
same availability zone of their network to confine the latency boundary of the
network traffic. The dividers shall span multiple availability zones to ensure
availability. That said,  the placement algorithm shall be flexible also to
place the bouncers across multiple availability zones to improve resiliency.
This is particularly important if the bouncers are serving scaled or proxied
endpoints. Such endpoints are usually used to implement network functions that
are regional or global,  and placement of the bouncers serving these endpoints
across multiple availability zones are essential for availability reasons.

Scaling objectives  of bouncers and dividers are to optimize the placement
decisions such that continuously
:

- **Control Network Congestion**:  By continuously increasing the number of
  bouncers needed to serve the network traffic.
- **Optimize Configuration Overhead and Cost Minimization**:  By continuously
  evaluating opportunities to scale down the number of bouncers and dividers
  within a network or VPC. Scaling down the number of bouncers shall not impact
  ongoing or expected traffic.

All of these objectives shall be satisfied while ensuring that the number of
bouncers and dividers shall always support an unexpected surge in traffic that
occur faster than the reacting time of scaling decision algorithm.

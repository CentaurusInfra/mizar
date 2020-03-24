## What is the primary use cases of Mizar?

Mizar provides a unified solution for computing runtimes (e.g., VM/Containers) networking in Cloud Computing. It is a step towards empowering super-scale cloud computing.

## What is a Mizar endpoint?

A Mizar endpoint is the virtual component sending or receiving traffic. That could be a virtual interface inside a container or a VM, a load-balancer, a NAT device, a gateway, or even a physical host. The endpoint can physically exist and run an application or virtually perform a specific function (e.g., a default network gateway).

## What is NOT a use case of Mizar?

Mizar is not a networking solution for data-centers, telecoms, ISPs, campus networks, etc. It only focuses on cloud networking. Thus,  Mizar's job starts when a packet arrives at the end host where the VM/container is running and ends as the packet leaves the host. Packets can still visit non-end hosts in transit.

## Is Mizar an NFV solution?

NFV is an overloaded term here. If we refer to NFV by providing software networking functions for multitenant cloud applications and networking, then Yes.  If NFV refers to telecoms, data-centers, ISPs, then the answer is No.

## What is a backplane in Mizar?

Mizar backplane is the elementary software that creates an overlay network of endpoints. Its primary function is traffic isolation, tunneling, and end-host discovery. The backplane job is to take the packet out of an endpoint and deliver it to another endpoint. It ensures isolating endpoints between multiple tenants. We designed the backplane to emphasis scale, performance, and dynamic endpoint provisioning. The backplane does not process the endpoint's packet, so it is not providing any useful network function to the endpoints.

## What is a data-plane in Mizar?

Mizar data plane is all the functions that process the endpoints packets. Thus providing networking services to container/VMs or any other compute type. These can be a load-balancer, a NAT device, ... etc.

## Which technology does the backplane use to create the tunnels?

We use Geneve and nothing else. It is excellent, extensible, simple, and has all that we need to build Mizar.

## Which technology the backplane use to forward packets?

We developed the backplane entirely in XDP and eBPF. It gives us fast IO without Kernel bypass and works nicely with the existing TCP/IP stack. We find that XDP provides a lot of high performance and concurrent data-structures (ebpf maps). Moreover, Jitting and code verification offers a safety mechanism to load XDP programs inside the Kernel. Thus, we can develop Mizar with excellent reliability as well as security guarantees.

## Why haven't you used DPDK?

DPDK would have been fine. Except that we see a lot of architectural benefits for the backplane to be implemented in XDP (in-kernel) or offloaded to SmartNICs. Moreover, we don't need to run separate user processes or allocate huge pages to perform very elementary functions. These approaches sound plausible to develop a dedicated network appliance that does not share resources with computing.

## Could you implement any of Mizar's components with DPDK?

Possibly. Some of the data-plane components may fit into a DPDK implementation. Such components are standalone by design and must not be integrated into Kernel, or offloaded to NICs. In such cases, the backplane shall either integrate with existing solutions or rebuilding such components from scratch.

## Could you have implemented any Mizar component with FD.IO/VPP then?

The same argument of DPDK applies here. We see benefits from in-kernel/ in-network processing through XDP.  We think of FD.IO/VPP primary use case to be container-based platforms for NFV. Nevertheless, the usage of VPP is still applicable for implementing data-plane standalone components.

## So you guys love XDP and eBPF, Could you have implemented any of Mizar components with AF_XDP then?

The same argument of DPDK and VPP applies again. It is userspace vs in-kernel architectural choice. But yes, when we extend to a standalone component, we will consider AF_XDP first. If we cannot reuse an existing solution and have to develop a particular component from scratch, we will adopt AF_XDP.

## How does the backplane scale?

Sharding. Sharding comes naturally to cloud networking, where tenant, network, and endpoint naturally partition configurations. By sharding network and configuration data across a few components, Mizar allows a management plane to push configuration almost in constant time to few numbers of nodes. So we shard tenants by VPCs and shard VPCs by networks (which is a group of endpoints). A management plane pushes VPC level configuration to a few nodes that we call Dividers and the network configurations to few nodes that we call Bouncers. Each VPC is designated a set of transit routes. And each network is designated to another set of Bouncers.

## So you are using virtual switches and virtual routers (and call them bouncers and dividers)?

No. The bouncers and dividers are nothing other than in-network lookup tables. They are abstract constructs that make it easy for a management plane to shard the configuration. But they don't exist or deployed separately. A virtual switch and routers have a notion of ports, L2, and L3 routing protocols. The bouncers and dividers don't do any of these. They are simply lookup tables to facilitate packet rewriting and create overlays.

## Isn't confining configuration to few nodes slows down packet forwarding?

Yes and No. In several scenarios, a packet needs to traverse multiple hosts to reach its final destination (in addition to usual hops in a data center network). So this adds latency. However, we found that these hops have minimal impact on end-to-end bandwidth and packet rate. Which especially true since with XDP packets, don't leave the device driver before being forwarded during transit (By the way, this is where the word transit comes from).  The latency is negligible if we optimally place the bouncers and dividers across nodes. For latency-sensitive applications, we are developing a fast-path feature that makes this latency impact on the first packet of the flow and nothing else.

## Couldn't have few bouncers or dividers limit the throughput for a large number of endpoints?

No. The bouncers and dividers auto-scales according to the total traffic volume in a network or VPC. Auto-scaling is still under development.

## So it is all about partitioning. Why don't you use Openvswitch, though?

Theoretically, we could. Practically, it is difficult. Openvswitch is a great project designed for so many use cases. The problem with its programming model for multitenant cloud-networking is that we need to stack multiple openvswitch in a complex architecture to achieve the same goal. Stacking multiple middle-boxes is the case of Neutron is one obvious example. We believe that the problem is that the designers have been trying to stitch Openvswitch in conventional network architecture (ports, L2 and L3 protocols). That programming model has made the control-plane job more difficult and hence complicated the control-plane design. In cloud networking and Mizar use case, it can be much more straightforward. Google hoverboard has made a similar argument, and we find it insightful.

## Is there a benefit then compared to OpenVswitch based solutions?

We found that if we focus on a specific use case (in our scope, it is cloud networking), we can get a much simplified and efficient design.  On a macro level, we can provision endpoints in almost constant time, while this would have been quadratic with the Openvswitch programming model.

## Why XDP again?

In addition to Fast IO, our initial assessment shows that Mizar requires a negligible memory footprint and CPU resources. On the other hand, an Openvswitch based solution would need at least 30% more memory and CPU on each host to do the same job as Mizar. Given the scale we aspire for, Mizar can have an accumulated resource-saving advantage.We also have greater flexibility in developing our business logic in XDP (c programming). Thus it is easier and more efficient to introduce sophisticated functions like fast-path that would have been difficult to implement with OpenVswitch.

## Why is the packet per second matching the line rate, while TCP bandwidth is clearly of subpar performance?

In our strawman, we used XDP with the generic mode driver only without a focus on performance. We took this approach to primarily verify functionality and necessary performance tests. We even introduced an undesirable kernel hack to do so. We are working on optimizations and more experiments with NICs that support driver mode.

## Okay, so you are done with the backplane. What's next?

See our [roadmap](releases/roadmap.md).
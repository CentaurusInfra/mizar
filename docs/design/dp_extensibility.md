Mizar facilitates the development of **Multi-tenant** networking functions at
various levels of the stack. The multi-tenant features mainly include reuse of
address space, traffic processing by the same functions, and traffic isolation
accorss multiple VPCs.

A network function is primarily an endpoint with the "bypass decapsulation" flag
set to allow the packet pipeline in Transit XDP to deliver the tunnel packets as
is so the function has designated access to tunnel metadata as well as the inner
packet. Most of the network functions will be scaled.

Network functions are either another XDP program or user space program
processing on the ingress of an endpoint (e.g., L7 Load-balancers).  Separating
the functions form the main Transit XDP program isolates the network functions
from the main packet processing pipeline and allow such functions to scale
independently of bouncers and dividers.

The performance requirements of the functions mainly influence the design choice
to develop a function as a separate XDP program or as a user-space program. For
example, functions that may run in hardware acceleration shall be XDP program to
match line-rate, especially on very high bandwidth NICs. The general guiding
design principle in this regard is:

"An in-network function shall add a negligible processing overhead to the main
packet processing pipeline, and must be critical to developing in the packet
pipeline."

Examples of these functions are Cross-VPC routing, VPC to the substrate router,
endpoint metadata injection/stripping, network ACLs.

## Packet-Processing Pipeline Extensilanebility

This Transit XDP design allows network functions to access the inner as well as
the outer packet headers and process the packets at the line-speed. The
following are a non-exhaustive list of network functions:

### Example Network Functions

* **Security**
    * Network Groups Policy Enforcement Points
    * DDoS Mitigation

* **Load Balancing**
    * L4 Load-balancer
    * L7 Load-balancer

* **Connectivity**
    * VPN
    * Nat
    * Cross-VPC routing

* **Traffic Shaping Control**
    * QoS
    * Rate limiting


## The Transit XDP Program

The Transit XDP program is running on the ingress path of the physical NIC of
the host and is capable of assuming either the Bouncer or the Divider roles
depending on the context of the flow processing.

The packet processing context determines the program's role of Bouncer or
Divider. The processing pipeline follows the following procedure:

1. If the ingress packets are not Geneve encapsulated, the transit XDP program
   passes the packet for standard processing to the Linux network stack.
1. If the destination endpoint belongs to a known IP address on the same host,
   activate an in-network packet processing stage. This stage can implement
   in-network functions for an endpoint such as NAT. The in-network processing
   can be bypassed or followed by redirect the packet to the corresponding veth
   egress. The redirection can be for the entire packet, or the decapsulated
   packet according to the processing context or type of the endpoint.
1. If the destination endpoint remote IP (host) is known, the Transit XDP
   program forwards the packet to the remote IP (Bouncer function)
1. If the destination endpoint's network is known, send the packet to one of the
   Bouncers of the network (Divider function) or another divider (in case of VPC
   to VPC peering) of the destination network based on source/destination words
   hashing. Otherwise, (network is not known), and if the program is the Divider
   of the VPC, drop the packet.
1. Forward the packet to one of the dividers of the VPC (Bouncer function).

The Transit XDP Program is extensible by several predefined stages in which the
program tail-calls another XDP program to process the packets. All programs
share the same ebpf maps, and hence state and configuration remain consistent.
Mizar currently supports the following stages

* ON_XDP_TX
* ON_XDP_PASS
* ON_XDP_REDIRECT
* ON_XDP_DROP
* ON_XDP_SCALED_EP

The following figure illustrates the packet flow inside the Transit XDP program:

![Packet Pipeline](png/packet_pipeline.png)





## Backplane

Architecturally the back-plane consists of a collection of **virtual transit devices**. The Geneve Internet-Draft defines a transit device as: " A forwarding element (e.g., router or switch) along the path of the tunnel making up a part of the Underlay Network.  A transit device MAY be capable of understanding the Geneve packet format but does not originate or terminate Geneve packets."

The three primary virtual transit devices of the backplane are transit agent, transit switch, and transit router.

* **Transit Agent:** is an endpoint's localhost gateway to the overlay network and provides necessary tunneling and networking services to the endpoint.

* **Transit Switch:** is a virtual tunnel switch that defines a network boundary within a VPC. It’s primarily responsible for forwarding traffic between endpoints of the same network.

* **Transit Router:** is another virtual device that routes traffic across the network boundaries (Transit Router — to — Transit Switch), as well as the VPC boundary (Transit Router — to — Transit Router, or to the Internet).

The below diagram illustrates the relationships between the transit agent, transit switch, and transit router.

```
                        VPC boundary

                             **
      network boundary       ||
                             ||
             *               ||
             |               ||
   +-----+   |     +-----+   ||     +-----+
   | EP  |   |     | EP  |   ||     | EP  |
+--+-----+-+ |  +--+-----+-+ ||  +--+-----+-+
| EP Agent | |  | EP Agent | ||  | EP Agent |
+-----^----+ |  +-----^----+ ||  +-----^----+
      |      |        |      ||        |
+-----+--+   | +------+-+    || +------+-+
|+----v--++  | |+-----v-++   || |+-----v-++
||+-------++ | ||+-------++  || ||+-------++
++|Transit | | ++|Transit |  || ++|Transit |
 ++ Switch | |  ++ Switch |  ||  ++ Switch |
  +--------+ |   +--------+  ||   +--------+
      ^      |        ^      ||        ^
      |      |        |      ||        |
      |      *        |      **        |
     +v---------------v+      +--------v-+
     | +---------------+-+    | +--------++
     | +-----------------+    | |+--------++
     | |                 |    | || Transit |
     +-+ Transit Router  |<---+->| Router  |
       |                 |      ++---------+
       +-----------------+
```

### Transit Agent

Each endpoint is associated with a transit agent. Some particular endpoint types (e.g., scaled endpoints) may be related to no transit agent at all or more than one agent. The transit agent carries out the following rules:

* Encapsulates the endpoint's egress traffic to one of the transit switches of the endpoint's network.
* Injects tunnel metadata in outer-packet as needed by the endpoint application type.
* May implement specific networking functions (e.g., Rate limiting, firewall, etc.).

With this architecture, the control-plane needs only to configure an endpoint's transit agent with the endpoint's network where the transit switches IPs are specified. The control-plane also configures the network's transit switches with the remote IPs of the endpoint (e.g., actual endpoint host) to allow flows to ingress to the endpoint.  This approach minimizes the configuration load required by the control-plane, hence reduces the endpoint (re)provisioning time.

### Transit Switch

Each network defines one or more transit switches. The control-plane dynamically tracks the list of transit switches according to the total traffic within the network. The transit switch roles are:

* Rewrite destination IPs of tunneled packets to its final destination host within a subnet.
* Forward packets to transit routers if the switch has no forwarding information about the flow.
* Injects tunnel metadata in outer-packet as necessary.
* Implements specific networking functions such as network ACLs, or responding to ARP on behalf of the endpoint.

The dynamic association of the transit switches to the network allows control-plane algorithms to optimize the overlay network performance metrics continuously (e.g., minimize latency, maximize throughput, or mitigate noisily neighbor effects).

### Transit Router

Each VPC defines one or more transit routers. Transit routers do not hold the remote IP configuration of endpoints and instead routes traffic between networks or VPCs. The transit router primary roles are:

* Forward packets to a network's transit switches within a VPC.
* Forward packets outside the VPC boundary (to other VPCs or the Internet).
* Inject/strip tunnel metadata in outer-packet.

## Data-plane

Mizar facilitates the development of **Multi-tenant** networking functions at various levels of the stack!

A network function is primarily an endpoint with the “bypass decapsulation” flag set to allow the back-plane pipeline to deliver the tunnel packets as is so the function has designated access to tunnel metadata as well as the inner packet. Most of the network functions will be scaled.

Network functions shall be primarily implemented as another XDP programs running on the ingress of an endpoint (e.g. L7 Load-balancers). This is required to provide the needed processing isolation of network functions from the main packet processing pipeline and allow such functions to scale independently of transit switches and routers.

Other functions may be developed as a packet processing step in the back-plane packet processing pipeline of the NIC ingress. The design choice to develop a function in-network or as a separate XDP program on the endpoint, is mainly influenced by the processing the criticality of the function. The general guiding design principle in this regard is:

“An in-network function shall add a negligible processing overhead to the main packet processing pipeline, and must be absolutely critical to developing in the backplane pipeline.”

Examples of these functions are Cross-VPC routing, VPC to the substrate router, endpoint metadata injection/stripping, network ACLs.

This backplane design allows network functions to access the inner as well as the outer packet headers and process the packets at the line-speed. The following are a non-exhaustive list of network functions that can be developed on top of Mizar backplane:

* **Security**
   - Network Groups Policy Enforcement Points
   - DDoS Mitigation

* **Load Balancing**
   - L4 Load-balancer
   - L7 Load-balancer

* **Connectivity**
   - VPN
   - Nat
   - Cross-VPC routing


* **Traffic Shaping Control**
   - QoS
   - Rate limiting

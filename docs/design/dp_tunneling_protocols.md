<!--
SPDX-License-Identifier: MIT
Copyright (c) 2020 The Authors.

Authors: Sherif Abdelwahab <@zasherif>
         Phu Tran          <@phudtran>

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

Several tunneling protocols can be used to implement an overlay network. We
choose Geneve as the main tunneling protocol at the moment and more tunneling
protocols shall be supported in future releases. Geneve is an emerged overlay
network standard that supports all the capabilities of VxLan, GRE, and STT. It
supports a large amount of metadata which will be required for data-plane
feature implementation and still ensures extensibility. Unlike VXLan and NVGRE,
which provides simple tunneling for underlay network partitioning, Geneve
provides the needed connectivity between multiple components of distributed
systems. This connectivity is required in order to implement various functions
of {name}. Several NICs are already supporting Geneve
encapsulation/decapsulation offloading. Also, Geneve supports randomized source
port over UDP, which allows consistent flow routing and processing among
multi-paths. We could use STT which provides similar functionality to Geneve,
but on TCP, thus Geneve remains preferred for its lower overhead.

### Geneve Packet format

The RFC draft
[VNO3-Geneve](https://www.ietf.org/id/draft-ietf-nvo3-geneve-13.txt) defines the
Geneve packet format. Geneve header can have a minimum length of 8 bytes and a
maximum of 260 bytes. The necessary fields to note in the Geneve header are:

* **Virtual Network Identifier (VNI):** In the standard, this can define an
  identifier for a unique element of a virtual network. In {name}, the VNI shall
  have the semantics of the VPC ID.
* **Opt Len:** The length of the options fields, expressed in multiples of four
  bytes, not including the eight bytes fixed tunnel header.

### Geneve Options

We shall be using Geneve TLV options to inject packet tunnel metadata that will
support the implementation of various network functions including network
policy, QoS, load balancing, NAT, … etc. For example, in the case of container
networking, we shall represent a label-selector as one Geneve option by which
policy enforcement points shall execute various decisions based on policy rules.
Also, the Geneve option shall encode the type of ​end-point, which shall alter
the routing decisions.
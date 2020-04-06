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

This architecture is extensible to derive other data-plane systems and is
compatible with existing cloud networking solutions (particularly neutron). For
example, if we would like to introduce a L2 ovs that is responsible for managing
a network overlay, we shall introduce a new object (e.g. L2Agent), and a new
operator (L2Operator). The L2Agent object will have multiple states to provision
OVS on each host. The L2Operator will be responsible for mutating the state of
existing objects using its knowledge about the current state of an OVS switch on
the host and the requriment of the mutated object and also program OVS through
direct RPC interface exposed by the transitd. For example when an endpoint is
provisioned the Network operator mutate the endpoint object with a list of all
the hosts of the network and move the endpoint object to L2-Agent-Ready state.
The L2Agent operator watches for endpoints in this state, and program all the
OVS in the relevant hosts with the appropriate flow-rules to ensure
connectivity.
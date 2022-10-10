<!--
SPDX-License-Identifier: MIT
Copyright (c) 2021 The Authors.

Authors:
Peng Yang               (@yangpenger)      

-->
Netronome SmartNIC has following limitations:

- Only supports maps of type BPF_MAP_TYPE_ARRAY/BPF_MAP_TYPE_HASH.
- Constrains the size of maps:
  - Sum of map entries on the NIC should be less than 3,072,000;
  - A maximum limit of 64 bytes per entry.
- Constrains the size of program: the maximum number of instructions on the SmartNIC is only 2800.
- Does not support XDP_REDIRECT.



Considering the limitations above, bouncers and dividers (forwarding function) are offloaded to the NIC. 



The first packet between two endpoints will pass through the bouncer/divider. This forwarding function will be implemented on the NIC. On the contrary, for the XDP program on the endpoint host's kernel, every packet (not only the first) will pass through it. The main function is to redirect rather than forward, so it is not the offloaded target.



The offloaded workflow is as follows (The black line represents the logic of the mizar, and the red line represents the partial function offloaded to SmartNIC):

![workflow of offloading XDP](offload_XDP_workflow.png)
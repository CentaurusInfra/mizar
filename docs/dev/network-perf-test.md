# How to test Mizar network performance
This document records the considerations of Mizar network performance testing, and the tools used and steps of processes in metric collecting.

Also, it has one sample collection of network metrics for the reference, which was the result of one of the basic performance testings.


## Background
Mizar is based on new technology of eBPF/XDP, provides brand new networking for containers. In order to evaluate Mizar's advantages, systematic process is desired to collect its network performance metric data, and compare with other network providers like Cilium and Calico.  


## Target network metrics
* TCP stream throughput (not to confuse with bandwidth)
* UDP PPS throughput
* Network latency


## Basic Test Process
Basic test is not for large scale and stress purpose; it only microscopes at communication between two endpoints.

### Test env setup
For its simplicity, Kind based K8S is recommended as the test env: 1 control plane node, 2 worker nodes: so-called Kind 1+2 env. The two pods involving in the test are deployed in anti-affinity mode.

### Throughput testing
iperf3 available in the testpod image is used. Run following commands to start iperf3 server:
```bash
kubectl run iperf-s --image=localhost:5000/testpod --overrides='{"spec":{"nodeName":"kind-worker"}}' -- iperf3 -s
```
Run following command to create iperf3 client:
```bash
kubectl run -it iperf-c --image=localhost:5000/testpod --overrides='{"spec":{"nodeName":"kind-worker2"}}' -- bash
```
To get TCP stream throughput:
```bash
iperf3 -c iperf-s -t 60
```
To get UDP PPS metrics:
```bash
iperf3 -c iperf-s -t 60 -u -b 1000M -l 64
```
After the throughput test is done, delete iperf3 server and client pods.

### Network latency testing
netperf tool is used to collect network latency metrics, in form of TCP_RR(request/response with 1 byte message body).
To start netperf server (netserver):
```bash
kubectl run np-s --image alectolytic/netperf --overrides='{"spec":{"nodeName":"kind-worker"}}'
```
To start netperf client, and test TCP/UDP latency:
```bash
kubectl run np-c --rm -it --image alectolytic/netperf --overrides='{"spec":{"nodeName":"kind-worker2"}}' -- /bin/sh
netperf -H np-s -l 60 -t TCP_RR -- -o min_latency,mean_latency,max_latency,stddev_latency,transaction_rate
```

### Sample network metrics in Kind 1+2 env
Kind host: AWS t2.xlarge (4 cpu, 16 GB mem, 40 GB disk), Ubuntu 20.04

| TCP stream throughput |
| --------------------- |
| 812 Mbps |

| UDP PPS | recv lost rate |
| ------- | -------------- |
| 31,166  | 0.57% |

| number of simultaneous connections | TCP_RR Latency in microseconds |
| ---------------------------------- | ------------------------ |
| 1  | 102.87 |
| 10 | 262.18 |
| 20 | 491.54 |
| 40 | 947.54 |                               

### Metrics collected with other providers
In the same Kind 1+2 env; same test processes as the above are followed.

#### Cilium
TODO

#### Calico
TODO


## Scale Test Process
TODO

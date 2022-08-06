<!--
SPDX-License-Identifier: MIT
Copyright (c) 2020 The Authors.

Authors: Vinay Kulkarni <@vinaykul>

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


# System Requirements

Mizar as a Kubernetes (K8s) Pod Networking solution is still in experimental and
developmental stages and has limited K8s version and OS version support.

At the time of writing this document, Mizar has the following requirements:
- Mizar has been tested with Kubernetes v1.21.0.
- Mizar currently works with Ubuntu Operating Systems version 18.04 and 20.04.
- Recommended node size: Atleast 4 CPUs, 16G memory, and 200Gb disk space.

**NOTE: For Ubuntu 18.04, Mizar bootstrap script will install a kernel version
that has the XDP support needed by Mizar. It is recommended that you use a test
cluster to run Mizar at this time.**


# Deploying the OS required for Mizar

Kubeadm is a K8s deployment tool that can easily bring up a Kubernetes cluster.
Before using kubeadm, we need to deploy two or more systems with either Ubuntu 20.04
(preferred) or Ubuntu 18.04. They can either be bare-metal systems (for experimenting
with eBPF offload NICs) or Virtual Machines deployed in AWS, GCE, or another VM
orchestration framework.

Deployment of the required OS version on the bare-metal or VM is out of the scope of
this document. Once the VMs are deployed and ready to use, it shows how to deploy
a 1-master 1-worker Kubernetes cluster and then how to deploy Mizar on it.

- In AWS, we have tested Mizar with AMI ID ami-01f87c43e618bf8f0 and t3.xlarge instance type.
- In GCP, we have tested Mizar with image ubuntu-2004-focal-v20211202 and n1-highmem-32 machine type.


# Kubernetes and Mizar Deployment Steps

This guide uses two t3.xlarge instance type VMs deployed in AWS (AMI ID ami-01f87c43e618bf8f0) as K8s
master and worker nodes with docker as container runtime.

1. SSH to K8s master and worker node VMs and bootstrap them for Mizar.

```bash
#
# ssh to K8s master node
#
ubuntu@ip-192-168-1-252:~$ wget https://raw.githubusercontent.com/CentaurusInfra/mizar/dev-next/bootstrap.sh -O /tmp/bootstrap.sh -o /dev/null
ubuntu@ip-192-168-1-252:~$
ubuntu@ip-192-168-1-252:~$ bash /tmp/bootstrap.sh
NOTE: This script will reboot the system if you opt to allow kernel update.
      If reboot is not required, it will log you out and require re-login for new permissions to take effect.

Press Ctrl-c to quit, any key to continue... 
...
...

```

```bash
#
# ssh to K8s worker node
#
ubuntu@ip-192-168-1-95:~$ wget https://raw.githubusercontent.com/CentaurusInfra/mizar/dev-next/bootstrap.sh -O /tmp/bootstrap.sh -o /dev/null
ubuntu@ip-192-168-1-95:~$ 
ubuntu@ip-192-168-1-95:~$ bash /tmp/bootstrap.sh 
NOTE: This script will reboot the system if you opt to allow kernel update.
      If reboot is not required, it will log you out and require re-login for new permissions to take effect.

Press Ctrl-c to quit, any key to continue... 
...
...

```

2. Install Kubernetes v1.21.0 binaries on master and worker nodes.

```bash
#
# K8s master node
#
ubuntu@ip-192-168-1-252:~$ sudo apt install apt-transport-https curl -y
ubuntu@ip-192-168-1-252:~$ curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
ubuntu@ip-192-168-1-252:~$ sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
ubuntu@ip-192-168-1-252:~$ sudo apt install kubeadm=1.21.0-00 kubelet=1.21.0-00 kubectl=1.21.0-00 kubernetes-cni -y
ubuntu@ip-192-168-1-252:~$ sudo apt-mark hold kubelet kubeadm kubectl

```

```bash
#
# K8s worker node
#
ubuntu@ip-192-168-1-95:~$ sudo apt install apt-transport-https curl -y
ubuntu@ip-192-168-1-95:~$ curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
ubuntu@ip-192-168-1-95:~$ sudo apt-add-repository "deb http://apt.kubernetes.io/ kubernetes-xenial main"
ubuntu@ip-192-168-1-95:~$ sudo apt install kubeadm=1.21.0-00 kubelet=1.21.0-00 kubernetes-cni -y
ubuntu@ip-192-168-1-95:~$ sudo apt-mark hold kubelet kubeadm

```

3. Create kubeadm configuration file on K8s master node.

```bash
#
# K8s master node
#
ubuntu@ip-192-168-1-252:~$ cat <<EOF >~/kubeadm-config.yaml
> kind: ClusterConfiguration
> apiVersion: kubeadm.k8s.io/v1beta2
> kubernetesVersion: v1.21.0
> ---
> kind: KubeletConfiguration
> apiVersion: kubelet.config.k8s.io/v1beta1
> cgroupDriver: systemd
> EOF

```

4. Initialize Kubernetes master node via **kubeadm init** and setup cluster configuration files.

```bash
#
# K8s master node
#
ubuntu@ip-192-168-1-252:~$ sudo kubeadm init --config ~/kubeadm-config.yaml
...
...
...
Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

kubeadm join 192.168.1.252:6443 --token dba3hs.okoqhtv7a67gpdfu \
	--discovery-token-ca-cert-hash sha256:2e26f770666c3a8bca97057671840d07f598b02d10d61c9889952c2cdb368a26 
ubuntu@ip-192-168-1-252:~$ 
ubuntu@ip-192-168-1-252:~$ mkdir -p $HOME/.kube
ubuntu@ip-192-168-1-252:~$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
ubuntu@ip-192-168-1-252:~$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
ubuntu@ip-192-168-1-252:~$

```

5. Join Kubernetes worker node to the cluster via kubeadm using the **join command** displayed by **kubeadm init**

```bash
#
# K8s worker node
#
ubuntu@ip-192-168-1-95:~$ sudo kubeadm join 192.168.1.252:6443 --token dba3hs.okoqhtv7a67gpdfu \
        --discovery-token-ca-cert-hash sha256:2e26f770666c3a8bca97057671840d07f598b02d10d61c9889952c2cdb368a26

```

6. Deploy Mizar Pod networking yaml from K8s master node.

```bash
#
# K8s master node
#
ubuntu@ip-192-168-1-252:~$ kubectl create -f https://github.com/CentaurusInfra/mizar/releases/download/v0.91/deploy.mizar.yaml

```


# Verifying Mizar Deployment

Mizar control plane is broadly defined by Kubernetes Custom Resource objects (CRDs) briefly
described below:
- **VPC**: This object describes the entire pod network space (IP CIDR range) for all the pods
  in the K8s cluster. A VPC may contain one or more **_Subnets_**.
- **Subnet**: This object represents the IP CIDR range for a group of pods that belong to the
  same subnetwork. This can be a subset of the VPC IP CIDR range.
- **Bouncer**: This object represents the cluster node that acts as switching agent for a group
  of K8s pods that belong to a **_Subnet_**, and is responsible for switching traffic between
  pods that belong to the same subnet. A subnet may have one or more bouncers depending on the
  traffic switching load.
- **Divider**: This object represents the cluster node that connects two or more **_Subnets_**.
  It is responsible for routing pod traffic between pods that span two different subnets.
- **Endpoint**: This object represents the connection point (interface) that connects a K8s pod
  or service to the subnet. Each endpoint belongs to a **_Bouncer_** and sends traffic to that
  bouncer in order to reach other pod or service endpoints.

When a cluster is brought up with Mizar, a default VPC and a default subnet are created.
They are named **vpc0** and **net0** respectively. Default VPC will have an initial default
number of Dividers provisioned. Similarly the default subnet will also have an initial
default number of Bouncers provisioned.

## Inspecting Mizar CRDs

There are two states for the resources listed below. *Init* and *Provisioned*. When a
resource is initially brought online, its state is set to *Init*. Once it has entered
the *Provisioned* state, the resource is officially up and ready for use.

You can inspect the Mizar resources by running the commands shown below.

 * Get all VPCs in the cluster

```bash
kubectl get vpcs
```

 * Get all Networks in the cluster

```bash
kubectl get subnets
```

 * Get all Dividers in the cluster

```bash
kubectl get dividers
```

 * Get all Bouncers in the cluster

```bash
kubectl get bouncers
```

 * Get all endpoints in the cluster

```bash
kubectl get endpoints
```

For more information on Mizar operations, please look at mizar-operator and mizar-daemon pod logs.


## Verifying Mizar Pod Network Connectivity

We can now deploy a simple network test pod to verify basic network connectivity. Please download
the test pod yaml from https://github.com/CentaurusInfra/mizar/wiki/Mizar-Cluster-Health-Criteria#test-pod-for-1-master-1-worker-cluster

```bash
#
# ssh to K8s master node
#
ubuntu@ip-192-168-1-252:~$ kubectl create -f ~/netpod.yaml 
pod/netpod1 created
pod/netpod2 created
ubuntu@ip-192-168-1-252:~$
ubuntu@ip-192-168-1-252:~$ kubectl get pods -owide
NAME                              READY   STATUS    RESTARTS   AGE   IP              NODE               NOMINATED NODE   READINESS GATES
mizar-daemon-4ql8r                1/1     Running   0          22m   192.168.1.252   ip-192-168-1-252   <none>           <none>
mizar-daemon-db2pz                1/1     Running   0          22m   192.168.1.95    ip-192-168-1-95    <none>           <none>
mizar-operator-757cb9d45f-bvcq9   1/1     Running   0          22m   192.168.1.95    ip-192-168-1-95    <none>           <none>
netpod1                           1/1     Running   0          51s   20.0.0.5        ip-192-168-1-95    <none>           <none>
netpod2                           1/1     Running   0          51s   20.0.0.4        ip-192-168-1-252   <none>           <none>
ubuntu@ip-192-168-1-252:~$ 
ubuntu@ip-192-168-1-252:~$ kubectl exec -ti netpod1 -- ping -c2 $(kubectl get pods -owide | grep netpod2 | awk '{print $6}')
PING 20.0.0.4 (20.0.0.4) 56(84) bytes of data.
64 bytes from 20.0.0.4: icmp_seq=1 ttl=64 time=0.423 ms
64 bytes from 20.0.0.4: icmp_seq=2 ttl=64 time=0.241 ms

--- 20.0.0.4 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1007ms
rtt min/avg/max/mdev = 0.241/0.332/0.423/0.091 ms
ubuntu@ip-192-168-1-252:~$ 

```

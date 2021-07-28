/*
Copyright 2021 The Mizar Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package main

import (
	"context"
	"flag"
	"fmt"
	"net"
	"path"
	"runtime"
	"strconv"
	"time"

	. "mizar.com/mizarcni/cmd/mizarcni/app"
	"mizar.com/mizarcni/pkg/object"
	"mizar.com/mizarcni/pkg/util/executil"
	"mizar.com/mizarcni/pkg/util/objectutil"

	"github.com/containernetworking/cni/pkg/skel"
	cniTypesVer "github.com/containernetworking/cni/pkg/types/current"
	"github.com/containernetworking/cni/pkg/version"
	"github.com/containernetworking/plugins/pkg/ns"
	"github.com/vishvananda/netlink"
	"golang.org/x/sys/unix"
	"google.golang.org/grpc"
	klog "k8s.io/klog/v2"
)

const (
	NetNSFolder = "/var/run/netns/"
)

var netVariables object.NetVariables
var podId PodId
var interfaceId InterfaceId

func init() {
	// Ensures runs only on main thread
	runtime.LockOSThread()

	klog.InitFlags(nil)
	flag.Set("logtostderr", "false")
	flag.Set("log_file", "/tmp/mizarcni.log")

	objectutil.LoadEnvVariables(&netVariables)
	info, err := objectutil.MountNetNSIfNeeded(&netVariables)
	klog.Info(info)
	if err != nil {
		klog.Fatal(err)
	}

	podId = PodId{
		K8SNamespace: netVariables.K8sPodNamespace,
		K8SPodName:   netVariables.K8sPodName,
		K8SPodTenant: netVariables.K8sPodTenant,
	}
	interfaceId = InterfaceId{
		PodId:     &podId,
		Interface: netVariables.IfName,
	}
}

func cmdAdd(args *skel.CmdArgs) error {
	if err := objectutil.LoadCniConfig(&netVariables, args.StdinData); err != nil {
		return err
	}
	klog.Infof("Network variables: %q", netVariables)

	// Construct a CniParameters grpc message
	param := CniParameters{
		PodId:     &podId,
		Netns:     netVariables.NetNS,
		Interface: netVariables.IfName,
	}
	klog.Infof("Doing CNI add for %s/%s", podId.K8SNamespace, podId.K8SPodName)
	client, conn, ctx, cancel, err := getInterfaceServiceClient()
	if err != nil {
		klog.Info(err)
		return err
	}
	defer conn.Close()
	defer cancel()

	// Consume new (and existing) interfaces for this Pod
	clientResult, err := client.ConsumeInterfaces(ctx, &param)
	if err != nil {
		klog.Info(err)
		return err
	}
	interfaces := clientResult.Interfaces

	if len(interfaces) == 0 {
		klog.Fatalf("No interfaces found for %s/%s", podId.K8SNamespace, podId.K8SPodName)
	}

	// Construct the result string
	result := cniTypesVer.Result{
		CNIVersion: netVariables.CniVersion,
	}
	for index, intf := range interfaces {
		if err = activateInterface(intf); err != nil {
			klog.Error(err)
			return err
		}

		result.Interfaces = append(result.Interfaces, &cniTypesVer.Interface{
			Name:    intf.InterfaceId.Interface,
			Mac:     intf.Address.Mac,
			Sandbox: netVariables.NetNS,
		})

		_, ipnet, err := net.ParseCIDR(fmt.Sprintf("%s/%d", intf.Address.IpAddress, 32))
		if err != nil {
			return err
		}
		result.IPs = append(result.IPs, &cniTypesVer.IPConfig{
			Version:   intf.Address.Version,
			Address:   *ipnet,
			Gateway:   net.ParseIP(intf.Address.GatewayIp),
			Interface: cniTypesVer.Int(index),
		})
	}
	return result.Print()
}

// moves the interface to the CNI netnt, rename it, set the IP address, and the GW.
func activateInterface(intf *Interface) error {
	klog.Infof("Activating interface: %q", intf)
	link, err := netlink.LinkByName(intf.Veth.Name)
	if err == nil {
		if link.Attrs().OperState == netlink.OperUp {
			klog.Infof("Interface %q has already been UP.", intf.Veth.Name)
			return nil
		}
	}

	netNS, err := ns.GetNS(netVariables.NetNS)
	_, netNSFileName := path.Split(netVariables.NetNS)
	if err != nil {
		klog.Errorf("Failed to open netns %q: %s", netVariables.NetNS, err)
		return err
	}
	defer netNS.Close()

	klog.Infof("Move interface %s/%d to netns %s", intf.Veth.Name, link.Attrs().Index, netNSFileName)
	if netlink.LinkSetNsFd(link, int(netNS.Fd())); err != nil {
		return err
	}
	if netlink.LinkSetName(link, netVariables.IfName); err != nil {
		return err
	}
	if err = netNS.Do(func(_ ns.NetNS) error {
		if err := netlink.LinkSetName(link, netVariables.IfName); err != nil {
			return err
		}

		loLink, err := netlink.LinkByName("lo")
		if err != nil {
			return err
		}
		if err = netlink.LinkSetUp(loLink); err != nil {
			return err
		}
		if err = netlink.LinkSetUp(link); err != nil {
			return err
		}

		ipPrefix, err := strconv.Atoi(intf.Address.IpPrefix)
		if err != nil {
			return err
		}
		ipConfig := &netlink.Addr{
			IPNet: &net.IPNet{
				IP:   net.ParseIP(intf.Address.IpAddress),
				Mask: net.CIDRMask(ipPrefix, 32),
			}}
		if err = netlink.AddrAdd(link, ipConfig); err != nil {
			return err
		}

		gw := net.ParseIP(intf.Address.GatewayIp)
		defaultRoute := netlink.Route{
			Dst:      nil,
			Gw:       gw,
			Protocol: unix.RTPROT_STATIC,
		}
		if err = netlink.RouteAdd(&defaultRoute); err != nil {
			return err
		}

		return nil
	}); err != nil {
		return err
	}

	klog.Info("Disable tso for pod")
	cmdTxt, result, err := executil.Execute("ip", "netns", "exec", netNSFileName, "ethtool", "-K", "eth0", "tso", "off", "gso", "off", "ufo", "off")
	klog.Infof("Executing cmd: \n%s\n%s", cmdTxt, result)
	if err != nil {
		return err
	}

	cmdTxt, result, err = executil.Execute("ip", "netns", "exec", netNSFileName, "ethtool", "--offload", "eth0", "rx", "off", "tx", "off")
	klog.Infof("Executing cmd: \n%s\n%s", cmdTxt, result)
	if err != nil {
		return err
	}

	klog.Infof("Successfully activated interface for %q", intf.InterfaceId.PodId)
	return nil
}

func cmdDel(args *skel.CmdArgs) error {
	if err := objectutil.LoadCniConfig(&netVariables, args.StdinData); err != nil {
		return err
	}
	klog.Infof("Network variables: %s", netVariables)

	param := CniParameters{
		PodId:     &podId,
		Netns:     netVariables.NetNS,
		Interface: netVariables.IfName,
	}

	client, conn, ctx, cancel, err := getInterfaceServiceClient()
	if err != nil {
		return err
	}
	defer conn.Close()
	defer cancel()

	_, err = client.DeleteInterface(ctx, &param)
	if err != nil {
		return err
	}

	netNS, _ := ns.GetNS(netVariables.NetNS)
	if netNS != nil {
		netNS.Close()
	}

	result := cniTypesVer.Result{}
	return result.Print()
}

func getInterfaceServiceClient() (InterfaceServiceClient, *grpc.ClientConn, context.Context, context.CancelFunc, error) {
	conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		return nil, nil, nil, nil, err
	}
	client := NewInterfaceServiceClient(conn)
	ctx, cancel := context.WithTimeout(context.Background(), time.Second*3)
	return client, conn, ctx, cancel, nil
}

func main() {
	defer klog.Flush()
	skel.PluginMain(cmdAdd, nil, cmdDel, version.PluginSupports("0.2.0", "0.3.0", "0.3.1"), "Mizar CNI plugin")
}

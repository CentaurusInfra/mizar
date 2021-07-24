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
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/containernetworking/cni/pkg/skel"
	"github.com/containernetworking/cni/pkg/types"
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

type NetVariables struct {
	command         string
	containerID     string
	netNS           string
	ifName          string
	cniPath         string
	k8sPodNamespace string
	k8sPodName      string
	k8sPodTenant    string
	cniVersion      string
	networkName     string
	plugin          string
}

var netVariables NetVariables
var podId PodId
var interfaceId InterfaceId

func init() {
	// Ensures runs only on main thread
	runtime.LockOSThread()

	klog.InitFlags(nil)
	flag.Set("logtostderr", "false")
	flag.Set("log_file", "/tmp/mizarcni.log")

	loadEnvVariables()
	podId = PodId{
		K8SNamespace: netVariables.k8sPodNamespace,
		K8SPodName:   netVariables.k8sPodName,
		K8SPodTenant: netVariables.k8sPodTenant,
	}
	interfaceId = InterfaceId{
		PodId:     &podId,
		Interface: netVariables.ifName,
	}
}

func cmdAdd(args *skel.CmdArgs) error {
	loadNetConf(args.StdinData)
	klog.Infof("Network variables: %q", netVariables)

	// Construct a CniParameters grpc message
	param := CniParameters{
		PodId:     &podId,
		Netns:     netVariables.netNS,
		Interface: netVariables.ifName,
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
		CNIVersion: netVariables.cniVersion,
	}
	for index, intf := range interfaces {
		if err = activateInterface(intf); err != nil {
			klog.Error(err)
			return err
		}

		result.Interfaces = append(result.Interfaces, &cniTypesVer.Interface{
			Name:    intf.InterfaceId.Interface,
			Mac:     intf.Address.Mac,
			Sandbox: netVariables.netNS,
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

	netNS, err := ns.GetNS(netVariables.netNS)
	_, netNSFileName := path.Split(netVariables.netNS)
	if err != nil {
		klog.Errorf("Failed to open netns %q: %s", netVariables.netNS, err)
		return err
	}
	defer netNS.Close()

	klog.Infof("Move interface %s/%d to netns %s", intf.Veth.Name, link.Attrs().Index, netNSFileName)
	if netlink.LinkSetNsFd(link, int(netNS.Fd())); err != nil {
		return err
	}
	if netlink.LinkSetName(link, netVariables.ifName); err != nil {
		return err
	}
	if err = netNS.Do(func(_ ns.NetNS) error {
		if err := netlink.LinkSetName(link, netVariables.ifName); err != nil {
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

	if err = execute(exec.Command("ip", "netns", "exec", netNSFileName, "ethtool", "-K", "eth0", "tso", "off", "gso", "off", "ufo", "off")); err != nil {
		return err
	}

	if err = execute(exec.Command("ip", "netns", "exec", netNSFileName, "ethtool", "--offload", "eth0", "rx", "off", "tx", "off")); err != nil {
		return err
	}

	klog.Infof("Successfully activated interface for %q", intf.InterfaceId.PodId)
	return nil
}

func removeIfFromNetNSIfExists(netNS ns.NetNS, ifName string) error {
	return netNS.Do(func(_ ns.NetNS) error {
		link, err := netlink.LinkByName(ifName)
		if err != nil {
			if strings.Contains(err.Error(), "Link not found") {
				return nil
			}
			return err
		}
		return netlink.LinkDel(link)
	})
}

func cmdDel(args *skel.CmdArgs) error {
	loadNetConf(args.StdinData)
	klog.Infof("Network variables: %s", netVariables)

	param := CniParameters{
		PodId:     &podId,
		Netns:     netVariables.netNS,
		Interface: netVariables.ifName,
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

	netNS, _ := ns.GetNS(netVariables.netNS)
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

func loadNetConf(bytes []byte) {
	netConf := &types.NetConf{}
	if err := json.Unmarshal(bytes, netConf); err != nil {
		if err != nil {
			klog.Fatalf("Failed to load netconf: %v", err)
		}
	}

	netVariables.cniVersion = netConf.CNIVersion
	netVariables.networkName = netConf.Name
	netVariables.plugin = netConf.Type
}

func loadEnvVariables() {
	netVariables.command = os.Getenv("CNI_COMMAND")
	netVariables.containerID = os.Getenv("CNI_CONTAINERID")
	netVariables.ifName = os.Getenv("CNI_IFNAME")
	netVariables.cniPath = os.Getenv("CNI_PATH")
	netVariables.netNS = mountNetNSIfNeeded(os.Getenv("CNI_NETNS"))

	cniArgs := os.Getenv("CNI_ARGS")
	if len(cniArgs) > 0 {
		splitted := strings.Split(cniArgs, ";")
		for _, item := range splitted {
			keyValue := strings.Split(item, "=")
			switch keyValue[0] {
			case "K8S_POD_NAMESPACE":
				netVariables.k8sPodNamespace = keyValue[1]
			case "K8S_POD_NAME":
				netVariables.k8sPodName = keyValue[1]
			case "K8S_POD_TENANT":
				netVariables.k8sPodTenant = keyValue[1]
			}
		}
	}
}

func mountNetNSIfNeeded(netNS string) string {
	if !strings.HasPrefix(netNS, NetNSFolder) {
		dstNetNS := strings.ReplaceAll(netNS, "/", "_")
		dstNetNSPath := filepath.Join(NetNSFolder, dstNetNS)
		if netVariables.command == "ADD" {
			os.Mkdir(NetNSFolder, os.ModePerm)
			os.Create(dstNetNSPath)
			if err := execute(exec.Command("mount", "--bind", netNS, dstNetNSPath)); err != nil {
				klog.Fatalf("failed to bind mount %s to %s: error code %s", netNS, dstNetNSPath, err)
			}
		}
		netNS = dstNetNSPath
	}
	return netNS
}

func execute(cmd *exec.Cmd) error {
	stdoutStderr, err := cmd.CombinedOutput()
	klog.Infof("Executing cmd: %s", cmd)
	klog.Infof("Cmd result: %s", stdoutStderr)
	if err != nil {
		return err
	}

	return nil
}

func main() {
	defer klog.Flush()
	skel.PluginMain(cmdAdd, nil, cmdDel, version.PluginSupports("0.2.0", "0.3.0", "0.3.1"), "Mizar CNI plugin")
}

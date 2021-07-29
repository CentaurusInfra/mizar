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
	"flag"
	"runtime"

	"centaurusinfra.io/mizar/pkg/object"
	"centaurusinfra.io/mizar/pkg/util/grpcclientutil"
	"centaurusinfra.io/mizar/pkg/util/netutil"
	"centaurusinfra.io/mizar/pkg/util/objectutil"

	"github.com/containernetworking/cni/pkg/skel"
	cniTypesVer "github.com/containernetworking/cni/pkg/types/current"
	"github.com/containernetworking/cni/pkg/version"
	klog "k8s.io/klog/v2"
)

const (
	NetNSFolder = "/var/run/netns/"
)

var netVariables object.NetVariables

func init() {
	// Ensures runs only on main thread
	runtime.LockOSThread()

	klog.InitFlags(nil)
	flag.Set("logtostderr", "false")
	flag.Set("log_file", "/tmp/mizarcni.log")

	objectutil.LoadEnvVariables(&netVariables)
	info, err := objectutil.MountNetNSIfNeeded(&netVariables)
	if info != "" {
		klog.Info(info)
	}
	if err != nil {
		klog.Fatal(err)
	}
}

func cmdAdd(args *skel.CmdArgs) error {
	if err := objectutil.LoadCniConfig(&netVariables, args.StdinData); err != nil {
		return err
	}
	klog.Infof("Network variables: %q", netVariables)

	klog.Infof("Doing CNI add for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName)
	interfaces, err := grpcclientutil.ConsumeInterfaces(netVariables)
	if err != nil {
		klog.Info(err)
		return err
	}
	if len(interfaces) == 0 {
		klog.Fatalf("No interfaces found for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName)
	}

	// Construct the result string
	result := cniTypesVer.Result{
		CNIVersion: netVariables.CniVersion,
	}
	for index, intf := range interfaces {
		klog.Infof("Activating interface: %q", intf)
		info, err := netutil.ActivateInterface(
			netVariables.IfName,
			netVariables.NetNS,
			intf.Veth.Name,
			intf.Address.IpPrefix,
			intf.Address.IpAddress,
			intf.Address.GatewayIp)
		if info != "" {
			klog.Info(info)
		}
		if err != nil {
			klog.Error(err)
			return err
		}

		result.Interfaces = append(result.Interfaces, &cniTypesVer.Interface{
			Name:    intf.InterfaceId.Interface,
			Mac:     intf.Address.Mac,
			Sandbox: netVariables.NetNS,
		})

		_, ipnet, err := netutil.ParseCIDR(intf.Address.IpAddress)
		if err != nil {
			return err
		}
		result.IPs = append(result.IPs, &cniTypesVer.IPConfig{
			Version:   intf.Address.Version,
			Address:   *ipnet,
			Gateway:   netutil.ParseIP(intf.Address.GatewayIp),
			Interface: cniTypesVer.Int(index),
		})
	}
	klog.Infof("Successfully activated interface for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName)
	return result.Print()
}

func cmdDel(args *skel.CmdArgs) error {
	if err := objectutil.LoadCniConfig(&netVariables, args.StdinData); err != nil {
		return err
	}
	klog.Infof("Network variables: %q", netVariables)

	err := grpcclientutil.DeleteInterface(netVariables)
	if err != nil {
		klog.Info(err)
		return err
	}

	netutil.DeleteNetNS(netVariables.NetNS)

	result := cniTypesVer.Result{}
	return result.Print()
}

func main() {
	defer klog.Flush()
	skel.PluginMain(cmdAdd, nil, cmdDel, version.PluginSupports("0.2.0", "0.3.0", "0.3.1"), "Mizar CNI plugin")
}

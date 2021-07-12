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
	"bufio"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"

	//interface_pb "mizar-cni/client"

	"github.com/containernetworking/cni/pkg/skel"
	"github.com/containernetworking/cni/pkg/types"
	cniTypesVer "github.com/containernetworking/cni/pkg/types/current"
	"github.com/containernetworking/cni/pkg/version"
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
	klog.Infof("Network variables: %s", netVariables)

	// Construct a CniParameters grpc message
	param := CniParameters{
		PodId:     &podId,
		Netns:     netVariables.netNS,
		Interface: netVariables.ifName,
	}
	klog.Infof("Doing CNI add for %s/%s", podId.K8SNamespace, podId.K8SPodName)
	// conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure(), grpc.WithBlock())
	// if err != nil {
	// 	return err
	// }
	// client := NewInterfaceServiceClient(conn)
	// ctx, cancel := context.WithTimeout(context.Background(), time.Second*3)
	client, conn, ctx, cancel, err := getInterfaceServiceClient()
	if err != nil {
		return err
	}
	defer conn.Close()
	defer cancel()
	clientResult, err := client.ConsumeInterfaces(ctx, &param)
	if err != nil {
		return err
	}
	interfaces := clientResult.Interfaces
	klog.Infof("hochan interfaces: %s", interfaces)

	if len(interfaces) == 0 {
		klog.Fatalf("No interfaces found for %s/%s", podId.K8SNamespace, podId.K8SPodName)
	}

	result := cniTypesVer.Result{
		CNIVersion: netVariables.cniVersion,
	}
	for index, interfaceItem := range interfaces {
		result.Interfaces = append(result.Interfaces, &cniTypesVer.Interface{
			Name:    interfaceItem.InterfaceId.Interface,
			Mac:     interfaceItem.Address.Mac,
			Sandbox: netVariables.netNS,
		})

		_, ipnet, err := net.ParseCIDR(fmt.Sprintf("%s/%s", interfaceItem.Address.IpAddress, interfaceItem.Address.IpPrefix))
		if err != nil {
			klog.Info("hochan error")
			return err
		}
		result.IPs = append(result.IPs, &cniTypesVer.IPConfig{
			Version:   interfaceItem.Address.Version,
			Address:   *ipnet,
			Gateway:   net.ParseIP(interfaceItem.Address.GatewayIp),
			Interface: cniTypesVer.Int(index),
		})
	}
	klog.Infof("hochan good: %s", result)
	return result.Print()
}

func cmdDel(args *skel.CmdArgs) error {
	loadNetConf(args.StdinData)
	klog.Infof("Network variables: %s", netVariables)

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
			klog.Fatalf("failed to load netconf: %v", err)
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
			os.Mkdir(dstNetNSPath, os.ModePerm)
			cmd := exec.Command("mount", "--bind", netNS, dstNetNSPath)
			stderr, _ := cmd.StderrPipe()
			cmd.Start()
			scanner := bufio.NewScanner(stderr)
			var strBuilder strings.Builder
			for scanner.Scan() {
				strBuilder.WriteString(scanner.Text())
			}
			err := cmd.Wait()
			if err != nil {
				klog.Fatalf("failed to bind mount %s to %s: error code %s: %s", netNS, dstNetNSPath, err, strBuilder.String())
			}
		}
		netNS = dstNetNSPath
	}
	return netNS
}

func main() {
	defer klog.Flush()
	skel.PluginMain(cmdAdd, nil, cmdDel, version.PluginSupports("0.2.0", "0.3.0", "0.3.1"), "Mizar CNI plugin")
}

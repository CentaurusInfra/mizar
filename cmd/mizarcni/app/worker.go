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

package app

import (
	"fmt"
	"strings"

	"centaurusinfra.io/mizar/pkg/object"
	"centaurusinfra.io/mizar/pkg/util/grpcclientutil"
	"centaurusinfra.io/mizar/pkg/util/netutil"
	"centaurusinfra.io/mizar/pkg/util/netvariablesutil"

	cniTypesVer "github.com/containernetworking/cni/pkg/types/current"
)

func DoInit(netVariables *object.NetVariables) (string, error) {
	netvariablesutil.LoadEnvVariables(netVariables)
	return netvariablesutil.MountNetNSIfNeeded(netVariables)
}

func DoCmdAdd(netVariables *object.NetVariables, stdinData []byte) (string, error) {
	strBuilder := strings.Builder{}

	if err := netvariablesutil.LoadCniConfig(netVariables, stdinData); err != nil {
		return strBuilder.String(), err
	}
	strBuilder.WriteString(fmt.Sprintf("Network variables: %s", netVariables))

	strBuilder.WriteString(fmt.Sprintf("\nDoing CNI add for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName))
	interfaces, err := grpcclientutil.ConsumeInterfaces(*netVariables)
	if err != nil {
		return strBuilder.String(), err
	}
	if len(interfaces) == 0 {
		return strBuilder.String(), fmt.Errorf("no interfaces found for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName)
	}

	// Construct the result string
	result := cniTypesVer.Result{
		CNIVersion: netVariables.CniVersion,
	}
	for index, intf := range interfaces {
		strBuilder.WriteString(fmt.Sprintf("\nActivating interface: %s", intf))
		info, err := netutil.ActivateInterface(
			netVariables.IfName,
			netVariables.NetNS,
			intf.Veth.Name,
			intf.Address.IpPrefix,
			intf.Address.IpAddress,
			intf.Address.GatewayIp)
		if info != "" {
			strBuilder.WriteString(fmt.Sprintf("\n%s", info))
		}
		if err != nil {
			return strBuilder.String(), err
		}

		result.Interfaces = append(result.Interfaces, &cniTypesVer.Interface{
			Name:    intf.InterfaceId.Interface,
			Mac:     intf.Address.Mac,
			Sandbox: netVariables.NetNS,
		})

		_, ipnet, err := netutil.ParseCIDR(intf.Address.IpAddress)
		if err != nil {
			return strBuilder.String(), err
		}
		result.IPs = append(result.IPs, &cniTypesVer.IPConfig{
			Version:   intf.Address.Version,
			Address:   *ipnet,
			Gateway:   netutil.ParseIP(intf.Address.GatewayIp),
			Interface: cniTypesVer.Int(index),
		})
	}

	return strBuilder.String(), result.Print()
}

func DoCmdDel(netVariables *object.NetVariables, stdinData []byte) (string, error) {
	strBuilder := strings.Builder{}

	if err := netvariablesutil.LoadCniConfig(netVariables, stdinData); err != nil {
		return strBuilder.String(), err
	}
	strBuilder.WriteString(fmt.Sprintf("Network variables: %s", netVariables))

	strBuilder.WriteString(fmt.Sprintf("\nDeleting interface for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName))
	err := grpcclientutil.DeleteInterface(*netVariables)
	if err != nil {
		return strBuilder.String(), err
	}

	strBuilder.WriteString(fmt.Sprintf("\nDeleting network namespace %s for interface of %s/%s", netVariables.NetNS, netVariables.K8sPodNamespace, netVariables.K8sPodName))
	info, err := netutil.DeleteNetNS(netVariables.NetNS)
	if info != "" {
		strBuilder.WriteString(fmt.Sprintf("\n%s", info))
	}
	if err != nil {
		return strBuilder.String(), err
	}

	result := cniTypesVer.Result{}
	return strBuilder.String(), result.Print()
}

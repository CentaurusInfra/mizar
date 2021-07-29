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

package objectutil

import (
	"encoding/json"
	"fmt"
	"path/filepath"
	"strings"

	"centaurusinfra.io/mizar/pkg/object"

	"centaurusinfra.io/mizar/pkg/util/executil"
	"centaurusinfra.io/mizar/pkg/util/osutil"
	"github.com/containernetworking/cni/pkg/types"
)

// Load cni config from args.StdinData
// Kubelet sends cni config through cmd argument. This func is to load them.
// Example data sent in: {"cniVersion":"0.3.1","name":"mizarcni","type":"mizarcni"}
func LoadCniConfig(netVariables *object.NetVariables, bytes []byte) error {
	netConf := &types.NetConf{}
	if err := json.Unmarshal(bytes, netConf); err != nil {
		if err != nil {
			return err
		}
	}

	netVariables.CniVersion = netConf.CNIVersion
	netVariables.NetworkName = netConf.Name
	netVariables.Plugin = netConf.Type
	return nil
}

func LoadEnvVariables(netVariables *object.NetVariables) {
	netVariables.Command = osutil.Getenv("CNI_COMMAND")
	netVariables.ContainerID = osutil.Getenv("CNI_CONTAINERID")
	netVariables.IfName = osutil.Getenv("CNI_IFNAME")
	netVariables.CniPath = osutil.Getenv("CNI_PATH")
	netVariables.NetNS = osutil.Getenv("CNI_NETNS")

	cniArgs := osutil.Getenv("CNI_ARGS")
	if len(cniArgs) > 0 {
		splitted := strings.Split(cniArgs, ";")
		for _, item := range splitted {
			keyValue := strings.Split(item, "=")
			switch keyValue[0] {
			case "K8S_POD_NAMESPACE":
				netVariables.K8sPodNamespace = keyValue[1]
			case "K8S_POD_NAME":
				netVariables.K8sPodName = keyValue[1]
			case "K8S_POD_TENANT":
				netVariables.K8sPodTenant = keyValue[1]
			}
		}
	}
}

func MountNetNSIfNeeded(netVariables *object.NetVariables) (string, error) {
	const NetNSFolder = "/var/run/netns/"
	info := ""
	if !strings.HasPrefix(netVariables.NetNS, NetNSFolder) {
		dstNetNS := strings.ReplaceAll(netVariables.NetNS, "/", "_")
		dstNetNSPath := filepath.Join(NetNSFolder, dstNetNS)
		if netVariables.Command == "ADD" {
			if osutil.FileExists(dstNetNSPath) {
				info = fmt.Sprintf("Skip mount %s since file %s exists.", netVariables.NetNS, dstNetNSPath)
			} else {
				osutil.Mkdir(NetNSFolder)
				osutil.Create(dstNetNSPath)
				cmdTxt, result, err := executil.Execute("mount", "--bind", netVariables.NetNS, dstNetNSPath)
				info = fmt.Sprintf("Executing cmd: \n%s\n%s", cmdTxt, result)
				if err != nil {
					return info, err
				}
			}
		}
		netVariables.NetNS = dstNetNSPath
	}

	return info, nil
}

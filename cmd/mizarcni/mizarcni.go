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

	"centaurusinfra.io/mizar/cmd/mizarcni/app"
	"centaurusinfra.io/mizar/pkg/object"

	"github.com/containernetworking/cni/pkg/skel"
	"github.com/containernetworking/cni/pkg/version"
	klog "k8s.io/klog/v2"
)

var netVariables object.NetVariables

func init() {
	// Ensures runs only on main thread
	runtime.LockOSThread()

	// Initial log
	klog.InitFlags(nil)
	flag.Set("logtostderr", "false")
	flag.Set("log_file", "/var/log/mizarcni.log")
	defer klog.Flush()
	klog.Infof("CNI_INIT: >>>>\n")

	result, err := app.DoInit(&netVariables)
	if result != "" {
		klog.Infof("CNI_INIT: Result: '%+v'\n", result)
	}
	if err != nil {
		klog.Errorf("CNI_INIT: Error: '%+v'\n", err)
	}
	klog.Infof("CNI_INIT: <<<<\n")
}

func cmdAdd(args *skel.CmdArgs) error {
	defer klog.Flush()
	klog.Infof("CNI_ADD: >>>> args: '%+v'\n", args)

	result, tracelog, err := app.DoCmdAdd(&netVariables, args.StdinData)
	if tracelog != "" {
		klog.Infof("CNI_ADD: Tracelog: '%+v'", tracelog)
	}
	if err != nil {
		klog.Errorf("CNI_ADD: Error: '%+v'\n", err)
	} else {
		klog.Infof("CNI_ADD: Success - interface added for pod '%s/%s'\n",
				netVariables.K8sPodNamespace, netVariables.K8sPodName)
	}
	klog.Infof("CNI_ADD: <<<<\n--------------------------------\n")
	result.Print()
	return err
}

func cmdDel(args *skel.CmdArgs) error {
	defer klog.Flush()
	klog.Infof("CNI_DEL: >>>> args: '%+v'\n", args)

	result, tracelog, err := app.DoCmdDel(&netVariables, args.StdinData)
	if tracelog != "" {
		klog.Infof("CNI_DEL: Tracelog: '%+v'", tracelog)
	}
	if err != nil {
		klog.Errorf("CNI_DEL: Error: '%+v'\n", err)
	} else {
		klog.Infof("CNI_DEL: Success - interface deleted for pod '%s/%s'\n",
				netVariables.K8sPodNamespace, netVariables.K8sPodName)
	}
	klog.Infof("CNI_DEL: <<<<\n--------------------------------\n")
	result.Print()
	return err
}

func main() {
	defer klog.Flush()
	skel.PluginMain(cmdAdd, nil, cmdDel, version.PluginSupports("0.2.0", "0.3.0", "0.3.1"), "Mizar CNI plugin")
}

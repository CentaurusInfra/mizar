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

	info, err := app.DoInit(&netVariables)
	if info != "" {
		klog.Info(info)
	}
	if err != nil {
		klog.Error(err)
	}
}

func cmdAdd(args *skel.CmdArgs) error {
	defer klog.Flush()

	info, err := app.DoCmdAdd(&netVariables, args.StdinData)
	if info != "" {
		klog.Info(info)
	}
	if err != nil {
		klog.Error(err)
		return err
	}

	klog.Infof("Successfully added interface for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName)
	return nil
}

func cmdDel(args *skel.CmdArgs) error {
	defer klog.Flush()

	info, err := app.DoCmdDel(&netVariables, args.StdinData)
	if info != "" {
		klog.Info(info)
	}
	if err != nil {
		klog.Error(err)
		return err
	}

	klog.Infof("Successfully deleted interface for %s/%s", netVariables.K8sPodNamespace, netVariables.K8sPodName)
	return nil
}

func main() {
	defer klog.Flush()
	skel.PluginMain(cmdAdd, nil, cmdDel, version.PluginSupports("0.2.0", "0.3.0", "0.3.1"), "Mizar CNI plugin")
}

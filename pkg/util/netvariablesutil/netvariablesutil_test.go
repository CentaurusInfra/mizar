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

package netvariablesutil_test

import (
	"errors"
	"os"
	"testing"

	"centaurusinfra.io/mizar/pkg/object"
	"centaurusinfra.io/mizar/pkg/util/executil"
	"centaurusinfra.io/mizar/pkg/util/netvariablesutil"
	"centaurusinfra.io/mizar/pkg/util/osutil"
	. "github.com/agiledragon/gomonkey/v2"
	. "github.com/smartystreets/goconvey/convey"
)

func Test_LoadCniConfig(t *testing.T) {
	Convey("Subject: netvariablesutil.LoadCniConfig", t, func() {
		Convey("Given correct input, get expected result", func() {
			netVariables := &object.NetVariables{}

			err := netvariablesutil.LoadCniConfig(netVariables, []byte("{\"cniVersion\":\"TestCniVersion\",\"name\":\"TestName\",\"type\":\"TestType\"}"))
			So(netVariables.CniVersion, ShouldEqual, "TestCniVersion")
			So(netVariables.NetworkName, ShouldEqual, "TestName")
			So(netVariables.Plugin, ShouldEqual, "TestType")
			So(err, ShouldBeNil)
		})

		Convey("Given wrong input, get expected result", func() {
			netVariables := &object.NetVariables{}

			err := netvariablesutil.LoadCniConfig(netVariables, []byte("[{\"Not_A_Field\":\"TestCniVersion\",\"name\":\"TestName\",\"type\":\"TestType\"}]"))
			So(err, ShouldNotBeNil)
		})
	})
}

func Test_LoadEnvVariables(t *testing.T) {
	Convey("Subject: netvariablesutil.LoadEnvVariables", t, func() {
		Convey("Given correct input, get expected result", func() {
			netVariables := &object.NetVariables{}
			patches := ApplyFunc(os.Getenv, func(key string) string {
				switch key {
				case "CNI_COMMAND":
					return "TestCNI_COMMAND"
				case "CNI_CONTAINERID":
					return "TestCNI_CONTAINERID"
				case "CNI_IFNAME":
					return "TestCNI_IFNAME"
				case "CNI_PATH":
					return "TestCNI_PATH"
				case "CNI_NETNS":
					return "TestCNI_NETNS"
				case "CNI_ARGS":
					return "K8S_POD_NAMESPACE=TestK8S_POD_NAMESPACE;K8S_POD_NAME=TestK8S_POD_NAME;K8S_POD_TENANT=TestK8S_POD_TENANT;Dummy=Dummy"
				default:
					return ""
				}
			})
			defer patches.Reset()

			netvariablesutil.LoadEnvVariables(netVariables)
			So(netVariables.Command, ShouldEqual, "TestCNI_COMMAND")
			So(netVariables.ContainerID, ShouldEqual, "TestCNI_CONTAINERID")
			So(netVariables.IfName, ShouldEqual, "TestCNI_IFNAME")
			So(netVariables.CniPath, ShouldEqual, "TestCNI_PATH")
			So(netVariables.NetNS, ShouldEqual, "TestCNI_NETNS")
			So(netVariables.K8sPodNamespace, ShouldEqual, "TestK8S_POD_NAMESPACE")
			So(netVariables.K8sPodName, ShouldEqual, "TestK8S_POD_NAME")
			So(netVariables.K8sPodTenant, ShouldEqual, "TestK8S_POD_TENANT")
		})

		Convey("Given empty input, get expected result", func() {
			netVariables := &object.NetVariables{}
			patches := ApplyFunc(os.Getenv, func(_ string) string {
				return ""
			})
			defer patches.Reset()

			netvariablesutil.LoadEnvVariables(netVariables)
			So(netVariables.Command, ShouldBeEmpty)
			So(netVariables.ContainerID, ShouldBeEmpty)
			So(netVariables.IfName, ShouldBeEmpty)
			So(netVariables.CniPath, ShouldBeEmpty)
			So(netVariables.NetNS, ShouldBeEmpty)
			So(netVariables.K8sPodNamespace, ShouldBeEmpty)
			So(netVariables.K8sPodName, ShouldBeEmpty)
			So(netVariables.K8sPodTenant, ShouldBeEmpty)
		})
	})
}

func Test_MountNetNSIfNeeded(t *testing.T) {
	Convey("Subject: netvariablesutil.MountNetNSIfNeeded", t, func() {
		Convey("Given normal NetNS, get expected result", func() {
			netNS := "/var/run/netns/TestNetNS"
			netVariables := &object.NetVariables{
				NetNS:   netNS,
				Command: "ADD",
			}

			info, err := netvariablesutil.MountNetNSIfNeeded(netVariables)
			So(info, ShouldBeEmpty)
			So(err, ShouldBeNil)
			So(netVariables.NetNS, ShouldEqual, netNS)
		})

		Convey("Given one word NetNS and Del command, get expected result", func() {
			netNS := "TestNetNS"
			netVariables := &object.NetVariables{
				NetNS:   netNS,
				Command: "DEL",
			}

			info, err := netvariablesutil.MountNetNSIfNeeded(netVariables)
			So(info, ShouldBeEmpty)
			So(err, ShouldBeNil)
			So(netVariables.NetNS, ShouldEqual, "/var/run/netns/TestNetNS")
		})

		Convey("Given multi words NetNS and Del command, get expected result", func() {
			netNS := "/tmp/TestNetNS"
			expectedNetNS := "/var/run/netns/_tmp_TestNetNS"
			netVariables := &object.NetVariables{
				NetNS:   netNS,
				Command: "DEL",
			}

			info, err := netvariablesutil.MountNetNSIfNeeded(netVariables)
			So(info, ShouldBeEmpty)
			So(err, ShouldBeNil)
			So(netVariables.NetNS, ShouldEqual, expectedNetNS)
		})

		Convey("Given multi words NetNS and Add command and Existing path, get expected result", func() {
			netNS := "/tmp/TestNetNS"
			expectedNetNS := "/var/run/netns/_tmp_TestNetNS"
			netVariables := &object.NetVariables{
				NetNS:   netNS,
				Command: "ADD",
			}
			patches := ApplyFunc(osutil.Exists, func(name string) bool {
				return name == expectedNetNS
			})
			defer patches.Reset()

			info, err := netvariablesutil.MountNetNSIfNeeded(netVariables)
			So(info, ShouldContainSubstring, "Skip mount /tmp/TestNetNS since file /var/run/netns/_tmp_TestNetNS exists")
			So(err, ShouldBeNil)
			So(netVariables.NetNS, ShouldEqual, expectedNetNS)
		})

		Convey("Given multi words NetNS and Add command and Non Existing path, get expected result", func() {
			netNS := "/tmp/TestNetNS"
			expectedNetNS := "/var/run/netns/_tmp_TestNetNS"
			netVariables := &object.NetVariables{
				NetNS:   netNS,
				Command: "ADD",
			}
			patches := ApplyFunc(osutil.Exists, func(name string) bool {
				return false
			})
			mkDirCalled := false
			patches.ApplyFunc(os.Mkdir, func(_ string, _ os.FileMode) error {
				mkDirCalled = true
				return nil
			})
			patches.ApplyFunc(os.Create, func(name string) (*os.File, error) {
				return nil, nil
			})
			patches.ApplyFunc(executil.Execute, func(_ string, _ ...string) (string, string, error) {
				return "Expected Cmd", "Expected Execution Result", nil
			})
			defer patches.Reset()

			info, err := netvariablesutil.MountNetNSIfNeeded(netVariables)
			So(info, ShouldContainSubstring, "Executing cmd")
			So(info, ShouldContainSubstring, "Expected Cmd")
			So(info, ShouldContainSubstring, "Expected Execution Result")
			So(mkDirCalled, ShouldBeTrue)
			So(err, ShouldBeNil)
			So(netVariables.NetNS, ShouldEqual, expectedNetNS)
		})

		Convey("Given execution error, get expected result", func() {
			netNS := "/tmp/TestNetNS"
			netVariables := &object.NetVariables{
				NetNS:   netNS,
				Command: "ADD",
			}
			patches := ApplyFunc(osutil.Exists, func(name string) bool {
				return false
			})
			mkDirCalled := false
			patches.ApplyFunc(os.Mkdir, func(_ string, _ os.FileMode) error {
				mkDirCalled = true
				return nil
			})
			patches.ApplyFunc(os.Create, func(name string) (*os.File, error) {
				return nil, nil
			})
			expectedError := errors.New("Expected Error")
			patches.ApplyFunc(executil.Execute, func(_ string, _ ...string) (string, string, error) {
				return "", "", expectedError
			})
			defer patches.Reset()

			info, err := netvariablesutil.MountNetNSIfNeeded(netVariables)
			So(info, ShouldContainSubstring, "Executing cmd")
			So(info, ShouldNotContainSubstring, "Expected Cmd")
			So(info, ShouldNotContainSubstring, "Expected Execution Result")
			So(mkDirCalled, ShouldBeTrue)
			So(err, ShouldEqual, expectedError)
			So(netVariables.NetNS, ShouldEqual, netNS)
		})
	})
}

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

package app_test

import (
	"errors"
	"net"
	"testing"

	"centaurusinfra.io/mizar/cmd/mizarcni/app"
	. "centaurusinfra.io/mizar/pkg/grpc"
	"centaurusinfra.io/mizar/pkg/object"
	"centaurusinfra.io/mizar/pkg/util/grpcclientutil"
	"centaurusinfra.io/mizar/pkg/util/netutil"
	"centaurusinfra.io/mizar/pkg/util/netvariablesutil"

	. "github.com/agiledragon/gomonkey/v2"
	. "github.com/smartystreets/goconvey/convey"
)

var netVariables object.NetVariables

func Test_DoInit(t *testing.T) {
	Convey("Subject: worker.DoInit", t, func() {
		Convey("Executed func and got expected result", func() {
			patches := ApplyFunc(netvariablesutil.LoadEnvVariables, func(netVariablesParam *object.NetVariables) {
				netVariablesParam.IfName = "Changed"
			})
			defer patches.Reset()
			expectedInfo := "Expected Info"
			expectedError := errors.New("Expected Error")
			patches.ApplyFunc(netvariablesutil.MountNetNSIfNeeded, func(_ *object.NetVariables) (string, error) {
				return expectedInfo, expectedError
			})

			info, err := app.DoInit(&netVariables)
			So(netVariables.IfName, ShouldEqual, "Changed")
			So(info, ShouldEqual, expectedInfo)
			So(err, ShouldEqual, expectedError)
		})
	})
}

func Test_DoCmdAdd(t *testing.T) {
	Convey("Subject: worker.DoCmdAdd", t, func() {
		Convey("Given LoadCniConfig error, got expected result", func() {
			expectedError := errors.New("Expected Error")
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return expectedError
			})
			defer patches.Reset()

			info, err := app.DoCmdAdd(&netVariables, nil)
			So(info, ShouldBeEmpty)
			So(err, ShouldEqual, expectedError)
		})

		Convey("Given ConsumeInterfaces error, got expected result", func() {
			expectedError := errors.New("Expected Error")
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return nil
			})
			patches.ApplyFunc(grpcclientutil.ConsumeInterfaces, func(_ object.NetVariables) ([]*Interface, error) {
				return nil, expectedError
			})
			defer patches.Reset()

			info, err := app.DoCmdAdd(&netVariables, nil)
			So(info, ShouldContainSubstring, "Network variables")
			So(info, ShouldContainSubstring, "Doing CNI add")
			So(err, ShouldEqual, expectedError)
		})

		Convey("Given empty interfaces, got expected result", func() {
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return nil
			})
			var interfaces []*Interface
			patches.ApplyFunc(grpcclientutil.ConsumeInterfaces, func(_ object.NetVariables) ([]*Interface, error) {
				return interfaces, nil
			})
			defer patches.Reset()

			info, err := app.DoCmdAdd(&netVariables, nil)
			So(info, ShouldContainSubstring, "Network variables")
			So(info, ShouldContainSubstring, "Doing CNI add")
			So(err.Error(), ShouldContainSubstring, "no interfaces found")
		})

		Convey("Given ActivateInterface error, got expected result", func() {
			expectedInfo := "Expected Info"
			expectedError := errors.New("Expected Error")
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return nil
			})
			var interfaces []*Interface
			interfaces = append(interfaces, &Interface{
				Veth:        &VethInterface{},
				Address:     &InterfaceAddress{},
				InterfaceId: &InterfaceId{},
			})
			patches.ApplyFunc(grpcclientutil.ConsumeInterfaces, func(_ object.NetVariables) ([]*Interface, error) {
				return interfaces, nil
			})
			patches.ApplyFunc(netutil.ActivateInterface, func(
				ifName string,
				netNSName string,
				vethName string,
				ipPrefix string,
				ipAddress string,
				gatewayIp string) (string, error) {
				return expectedInfo, expectedError
			})
			defer patches.Reset()

			info, err := app.DoCmdAdd(&netVariables, nil)
			So(info, ShouldContainSubstring, "Network variables")
			So(info, ShouldContainSubstring, "Doing CNI add")
			So(info, ShouldContainSubstring, "Activating interface")
			So(info, ShouldContainSubstring, expectedInfo)
			So(err, ShouldEqual, expectedError)
		})

		Convey("Given ParseCIDR error, got expected result", func() {
			expectedInfo := "Expected Info"
			expectedError := errors.New("Expected Error")
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return nil
			})
			var interfaces []*Interface
			interfaces = append(interfaces, &Interface{
				Veth:        &VethInterface{},
				Address:     &InterfaceAddress{},
				InterfaceId: &InterfaceId{},
			})
			patches.ApplyFunc(grpcclientutil.ConsumeInterfaces, func(_ object.NetVariables) ([]*Interface, error) {
				return interfaces, nil
			})
			patches.ApplyFunc(netutil.ActivateInterface, func(
				ifName string,
				netNSName string,
				vethName string,
				ipPrefix string,
				ipAddress string,
				gatewayIp string) (string, error) {
				return expectedInfo, nil
			})
			patches.ApplyFunc(netutil.ParseCIDR, func(s string) (net.IP, *net.IPNet, error) {
				return nil, nil, expectedError
			})
			defer patches.Reset()

			info, err := app.DoCmdAdd(&netVariables, nil)
			So(info, ShouldContainSubstring, "Network variables")
			So(info, ShouldContainSubstring, "Doing CNI add")
			So(info, ShouldContainSubstring, "Activating interface")
			So(info, ShouldContainSubstring, expectedInfo)
			So(err, ShouldEqual, expectedError)
		})

		Convey("Given no error, got expected result", func() {
			expectedInfo := "Expected Info"
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return nil
			})
			var interfaces []*Interface
			interfaces = append(interfaces, &Interface{
				Veth:        &VethInterface{},
				Address:     &InterfaceAddress{},
				InterfaceId: &InterfaceId{},
			})
			patches.ApplyFunc(grpcclientutil.ConsumeInterfaces, func(_ object.NetVariables) ([]*Interface, error) {
				return interfaces, nil
			})
			patches.ApplyFunc(netutil.ActivateInterface, func(
				ifName string,
				netNSName string,
				vethName string,
				ipPrefix string,
				ipAddress string,
				gatewayIp string) (string, error) {
				return expectedInfo, nil
			})
			var ipnet net.IPNet
			patches.ApplyFunc(netutil.ParseCIDR, func(s string) (net.IP, *net.IPNet, error) {
				return nil, &ipnet, nil
			})
			defer patches.Reset()

			info, err := app.DoCmdAdd(&netVariables, nil)
			So(info, ShouldContainSubstring, "Network variables")
			So(info, ShouldContainSubstring, "Doing CNI add")
			So(info, ShouldContainSubstring, "Activating interface")
			So(info, ShouldContainSubstring, expectedInfo)
			So(err, ShouldBeNil)
		})
	})
}

func Test_DoCmdDel(t *testing.T) {
	Convey("Subject: worker.DoCmdDel", t, func() {
		Convey("Given LoadCniConfig error, got expected result", func() {
			expectedError := errors.New("Expected Error")
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return expectedError
			})
			defer patches.Reset()

			info, err := app.DoCmdDel(&netVariables, nil)
			So(info, ShouldBeEmpty)
			So(err, ShouldEqual, expectedError)
		})

		Convey("Given DeleteInterface error, got expected result", func() {
			expectedError := errors.New("Expected Error")
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return nil
			})
			patches.ApplyFunc(grpcclientutil.DeleteInterface, func(_ object.NetVariables) error {
				return expectedError
			})
			defer patches.Reset()

			info, err := app.DoCmdDel(&netVariables, nil)
			So(info, ShouldContainSubstring, "Network variables")
			So(info, ShouldContainSubstring, "Deleting interface")
			So(err, ShouldEqual, expectedError)
		})

		Convey("Given no error, got expected result", func() {
			patches := ApplyFunc(netvariablesutil.LoadCniConfig, func(_ *object.NetVariables, _ []byte) error {
				return nil
			})
			patches.ApplyFunc(grpcclientutil.DeleteInterface, func(_ object.NetVariables) error {
				return nil
			})
			defer patches.Reset()

			info, err := app.DoCmdDel(&netVariables, nil)
			So(info, ShouldContainSubstring, "Network variables")
			So(info, ShouldContainSubstring, "Deleting interface")
			So(info, ShouldContainSubstring, "Deleting network namespace")
			So(err, ShouldBeNil)
		})
	})
}

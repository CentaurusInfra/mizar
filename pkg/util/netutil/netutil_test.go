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

package netutil_test

import (
	"strings"
	"testing"

	"centaurusinfra.io/mizar/pkg/util/executil"
	"centaurusinfra.io/mizar/pkg/util/netutil"
	"github.com/containernetworking/plugins/pkg/ip"
	"github.com/containernetworking/plugins/pkg/ns"
	"github.com/containernetworking/plugins/pkg/testutils"
	. "github.com/smartystreets/goconvey/convey"
)

// The test cases in this package need sudo permission
// It cannot be executed successfully in environments such as Visual Studio Code
// Can be executed by example command "sudo /usr/local/go/bin/go test /home/ubuntu/go/src/k8s.io/mizar/pkg/util/netutil/netutil_test.go"
// To execute all go test, example command is "sudo /usr/local/go/bin/go test /home/ubuntu/go/src/k8s.io/mizar/..."

func Test_ActivateInterface(t *testing.T) {
	Convey("Subject: netutil.ActivateInterface", t, func() {
		ifName := "eth-894cad92"
		var netNSNameToClear string

		Convey("Given interface is up, get expected result", func() {
			netNS, netNSName := createNetNS()
			t.Log(netNSName)
			netNSNameToClear = netNSName
			_, err := ns.GetNS("/var/run/netns/" + netNSName)
			So(err, ShouldBeNil)

			hostVeth, _, err := ip.SetupVeth(ifName, 1500, netNS)
			So(err, ShouldBeNil)

			log, err := netutil.ActivateInterface(
				hostVeth.Name,
				netNSName,
				ifName,
				"16",
				"10.20.0.81",
				"10.20.0.1")
			So(err, ShouldBeNil)
			So(log, ShouldEqual, "Interface 'eth-894cad92' already UP.")
		})

		Reset(func() {
			executil.Execute("ip", "link", "delete", ifName)
			netutil.DeleteNetNS(netNSNameToClear)
		})
	})
}

func Test_DeleteNetNS(t *testing.T) {
	Convey("Subject: netutil.DeleteNetNS", t, func() {
		Convey("Given correct input, get expected result", func() {
			_, netNSName := createNetNS()
			_, exeResult, _ := executil.Execute("ip", "netns", "ls")
			So(exeResult, ShouldContainSubstring, netNSName)

			netutil.DeleteNetNS(netNSName)

			_, exeResult, _ = executil.Execute("ip", "netns", "ls")
			So(exeResult, ShouldNotContainSubstring, netNSName)
		})

		Convey("Given wrong input, no error thrown", func() {
			So(func() { netutil.DeleteNetNS("Dummy Network Namespace") }, ShouldNotPanic)
		})
	})
}

func createNetNS() (ns.NetNS, string) {
	netNS, _ := testutils.NewNS()
	pathes := strings.Split(netNS.Path(), "/")
	return netNS, pathes[len(pathes)-1]
}

func Test_ParseCIDR(t *testing.T) {
	Convey("Subject: netutil.ParseCIDR", t, func() {
		Convey("Given correct input, get expected result", func() {
			ip, ipNet, err := netutil.ParseCIDR("10.20.0.8/16")
			So(ip.String(), ShouldEqual, "10.20.0.8")
			So(ipNet.String(), ShouldEqual, "10.20.0.0/16")
			So(err, ShouldBeNil)
		})

		Convey("Given no mask, get expected result", func() {
			ip, ipNet, err := netutil.ParseCIDR("10.20.0.8")
			So(ip.String(), ShouldEqual, "10.20.0.8")
			So(ipNet.String(), ShouldEqual, "10.20.0.8/32")
			So(err, ShouldBeNil)
		})

		Convey("Given wrong input, get error", func() {
			ip, ipNet, err := netutil.ParseCIDR("256.0.0.8/16")
			So(ip, ShouldBeNil)
			So(ipNet, ShouldBeNil)
			So(err, ShouldNotBeNil)
		})
	})
}

func Test_ParseIP(t *testing.T) {
	Convey("Subject: netutil.ParseIP", t, func() {
		Convey("Given correct input, get expected result", func() {
			ip := netutil.ParseIP("10.20.0.8")
			So(ip.String(), ShouldEqual, "10.20.0.8")
		})

		Convey("Given wrong input, get nil", func() {
			ip := netutil.ParseIP("10.20.0.8/16")
			So(ip, ShouldBeNil)
		})
	})
}

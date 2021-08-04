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
	"github.com/containernetworking/plugins/pkg/testutils"
	. "github.com/smartystreets/goconvey/convey"
)

// The test cases in this package need sudo permission
// It cannot be executed successfully in environments such as Visual Studio Code
// Can be executed by command "sudo /usr/local/go/bin/go test /home/ubuntu/go/src/k8s.io/mizar/pkg/util/netutil/netutil_test.go"

func Test_DeleteNetNS(t *testing.T) {
	Convey("Subject: netutil.DeleteNetNS", t, func() {
		Convey("Given correct input, get expected result", func() {
			netNS, _ := testutils.NewNS()
			pathes := strings.Split(netNS.Path(), "/")
			netNSName := pathes[len(pathes)-1]

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

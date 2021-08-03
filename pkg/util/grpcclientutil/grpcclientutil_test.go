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

package grpcclientutil_test

import (
	"testing"

	"centaurusinfra.io/mizar/pkg/object"
	"centaurusinfra.io/mizar/pkg/util/grpcclientutil"
	. "github.com/smartystreets/goconvey/convey"
)

func Test_GenerateCniParameters(t *testing.T) {
	Convey("Subject: grpcclientutil.GenerateCniParameters", t, func() {
		Convey("Given correct input, get expected result", func() {
			netVariables := object.NetVariables{
				K8sPodNamespace: "TestK8sPodNamespace",
				K8sPodName:      "TestK8sPodName",
				K8sPodTenant:    "TestK8sPodTenant",
				NetNS:           "TestNetNS",
				IfName:          "TestIfName",
			}

			cniParameters := grpcclientutil.GenerateCniParameters(netVariables)
			So(cniParameters.PodId.K8SNamespace, ShouldEqual, "TestK8sPodNamespace")
		})
	})
}

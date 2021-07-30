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

package executil_test

import (
	"testing"

	"centaurusinfra.io/mizar/pkg/util/executil"
	"centaurusinfra.io/mizar/pkg/util/osutil"
	. "github.com/smartystreets/goconvey/convey"
)

func TestSpec(t *testing.T) {
	Convey("Subject: executil.Execute", t, func() {

		Convey("Given correct input, expecting success", func() {
			cmdTxt, result, err := executil.Execute("mkdir", "-p", "/tmp/test_folder")
			So(err, ShouldBeNil)
			So(cmdTxt, ShouldContainSubstring, "mkdir -p /tmp/test_folder")
			So(result, ShouldBeEmpty)

			cmdTxt, result, err = executil.Execute("touch", "/tmp/test_folder/test_file")
			So(err, ShouldBeNil)
			So(cmdTxt, ShouldContainSubstring, "touch /tmp/test_folder/test_file")
			So(result, ShouldBeEmpty)
			So(osutil.FileExists("/tmp/test_folder/test_file"), ShouldEqual, true)

			cmdTxt, result, err = executil.Execute("ls", "/tmp/test_folder/")
			So(err, ShouldBeNil)
			So(cmdTxt, ShouldContainSubstring, "ls /tmp/test_folder/")
			So(result, ShouldEqual, "test_file\n")

			cmdTxt, result, err = executil.Execute("rm", "-rf", "/tmp/test_folder")
			So(err, ShouldBeNil)
			So(cmdTxt, ShouldContainSubstring, "rm -rf /tmp/test_folder")
			So(result, ShouldBeEmpty)
			So(osutil.FileExists("/tmp/test_folder/test_file"), ShouldEqual, false)
		})

		Convey("Given wrong input, expecting error", func() {
			cmdTxt, result, err := executil.Execute("mkdir", "/tmp/test_folder/new1/new2")
			So(err, ShouldNotBeNil)
			So(err.Error(), ShouldEqual, "exit status 1")
			So(cmdTxt, ShouldContainSubstring, "mkdir /tmp/test_folder/new1/new2")
			So(result, ShouldEqual, "mkdir: cannot create directory ‘/tmp/test_folder/new1/new2’: No such file or directory\n")
		})
	})
}

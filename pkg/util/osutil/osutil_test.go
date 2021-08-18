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

package osutil_test

import (
	"testing"

	"centaurusinfra.io/mizar/pkg/util/executil"
	"centaurusinfra.io/mizar/pkg/util/osutil"
	. "github.com/smartystreets/goconvey/convey"
)

func Test_Getenv(t *testing.T) {
	Convey("Subject: osutil.Getenv", t, func() {

		Convey("Given correct input, expecting success", func() {
			So(osutil.Getenv("PATH"), ShouldContainSubstring, "/usr/bin")
		})

		Convey("Given wrong input, expecting empty", func() {
			So(osutil.Getenv("Non_Exists_Environment_Variable"), ShouldBeEmpty)
		})
	})
}

func Test_Exists(t *testing.T) {
	Convey("Subject: osutil.Exists", t, func() {

		executil.Execute("mkdir", "-p", "/tmp/test_folder")

		Convey("Given existing folder name, returns true", func() {
			So(osutil.Exists("/tmp/test_folder"), ShouldBeTrue)
			So(osutil.Exists("/tmp/test_folder/"), ShouldBeTrue)
		})

		Convey("Given non existing folder name, returns false", func() {
			executil.Execute("rm", "-rf", "/tmp/test_folder")
			So(osutil.Exists("/tmp/test_folder"), ShouldBeFalse)
			So(osutil.Exists("/tmp/test_folder/"), ShouldBeFalse)
		})

		Convey("Given existing file name, returns true", func() {
			executil.Execute("touch", "/tmp/test_folder/test_file")
			So(osutil.Exists("/tmp/test_folder/test_file"), ShouldBeTrue)
		})

		Convey("Given non existing file name, returns false", func() {
			So(osutil.Exists("/tmp/test_folder/test_file"), ShouldBeFalse)
		})

		Reset(func() {
			executil.Execute("rm", "-rf", "/tmp/test_folder")
		})
	})
}

func Test_Mkdir(t *testing.T) {
	Convey("Subject: osutil.Mkdir", t, func() {

		Convey("Given correct input, expecting success", func() {
			osutil.Mkdir("/tmp/test_folder")
			So(osutil.Exists("/tmp/test_folder"), ShouldBeTrue)
		})

		Convey("Given wrong input, expecting nothing happened", func() {
			osutil.Mkdir("/tmp/test_folder/test_file")
			So(osutil.Exists("/tmp/test_folder/test_file"), ShouldBeFalse)
		})

		Reset(func() {
			executil.Execute("rm", "-rf", "/tmp/test_folder")
		})
	})
}

func Test_Create(t *testing.T) {
	Convey("Subject: osutil.Create", t, func() {

		executil.Execute("mkdir", "-p", "/tmp/test_folder")

		Convey("Given correct input, expecting success", func() {
			osutil.Create("/tmp/test_folder/test_file")
			So(osutil.Exists("/tmp/test_folder/test_file"), ShouldBeTrue)
		})

		Convey("Given wrong input, expecting nothing happened", func() {
			osutil.Create("/tmp/test_folder/dummy_folder/test_file")
			So(osutil.Exists("/tmp/test_folder/dummy_folder/test_file"), ShouldBeFalse)
		})

		Reset(func() {
			executil.Execute("rm", "-rf", "/tmp/test_folder")
		})
	})
}

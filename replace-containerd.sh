#!/bin/bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2022 The Authors.

# Authors: The Mizar Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

function main {
  cd $HOME/go/src/k8s.io/arktos
  wget -qO- https://github.com/CentaurusInfra/containerd/releases/download/tenant-cni-args/containerd.zip | zcat > /tmp/containerd
  sudo chmod +x /tmp/containerd
  sudo systemctl stop containerd
  sudo mv /usr/bin/containerd /usr/bin/containerd.bak
  sudo mv /tmp/containerd /usr/bin/
  sudo systemctl restart containerd
  sudo systemctl restart docker
}

if [[ "$(arch)" == "x86_64" ]]; then
  main
else
  echo "CPU architecture $(arch) not supported."
fi

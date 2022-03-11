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

function update-kernel-for-mizar {
  kernel_dir="/tmp/linux-5.6-rc2"
  mkdir -p $kernel_dir

  wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-headers-5.6.0-rc2_5.6.0-rc2-1_amd64.deb -P $kernel_dir
  wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-image-5.6.0-rc2-dbg_5.6.0-rc2-1_amd64.deb -P $kernel_dir
  wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-image-5.6.0-rc2_5.6.0-rc2-1_amd64.deb -P $kernel_dir
  wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-libc-dev_5.6.0-rc2-1_amd64.deb -P $kernel_dir
  sudo dpkg -i $kernel_dir/*.deb

  read -p "Reboot host now? (y/n)?" choice
  case "$choice" in
    y|Y ) echo "Rebooting...";;
    n|N ) echo "Please reboot for updated kernel to take effect."; return;;
    * ) return;;
  esac

  sudo reboot
}

function check-and-install-mizar-kernel {
  kernel_ver=$(uname -r)
  kernel_header_ver=$(sudo apt list linux-headers-$(uname -r) | grep "linux-headers-" | cut -d/ -f1 | sed 's/linux-headers-//')
  echo "Currently running kernel version: $kernel_ver"
  echo "Currently running kernel header version: $kernel_header_ver"
  echo ".................................................."

  mj_ver=$(echo $kernel_ver | cut -d. -f1)
  mn_ver=$(echo $kernel_ver | cut -d. -f2)
  if ([ "$mj_ver" -lt 5 ]) || ([ "$mj_ver" -eq 5 ] && [ "$mn_ver" -le 5 ]); then
    tput setaf 1
    echo "Mizar requires an updated kernel: linux-5.6 rc2 for TCP to function correctly. Current version is $kernel_ver"
    read -p "Execute kernel update script (y/n)?" choice
    tput sgr0
    case "$choice" in
      y|Y ) update-kernel-for-mizar;;
      n|N ) echo "Please run kernelupdate.sh to download and update the kernel!"; return;;
      * ) echo "Please run kernelupdate.sh to download and update the kernel!"; return;;
    esac
  fi

  if [[ "$kernel_ver" != "$kernel_header_ver" ]]; then
    tput setf 2
    echo " Updating kernel_header.."
    tput sgr0
    sudo apt-get install linux-headers-$(uname -r) -y
  fi
}

# Main
check-and-install-mizar-kernel

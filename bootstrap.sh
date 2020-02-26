#!/bin/bash

sudo apt-get update
sudo apt-get install -y \
    build-essential clang-7 llvm-7 \
    libelf-dev \
    python3 \
    python3-pip \
    libcmocka-dev \
    lcov

sudo apt install docker.io
sudo pip3 install netaddr docker scapy
sudo systemctl unmask docker.service
sudo systemctl unmask docker.socket
sudo systemctl start docker
sudo systemctl enable docker

sudo docker build -f ./test/Dockerfile -t buildbox:v2 ./test

git submodule update --init --recursive

kernel_ver=`uname -r`
echo "Running kernel version: $kernel_ver"

if [ "$kernel_ver" != "5.6.0-rc2" ]; then
	echo "Mizar requires an updated kernel: linux-5.6-rc2 for TCP to function correctly. Current version is $kernel_ver"

	read -p "Execute kernel update script (y/n)?" choice
	case "$choice" in
	  y|Y ) sh ./kernelupdate.sh;;
	  n|N ) echo "Please run kernelupdate.sh to download and update the kernel!"; exit;;
	  * ) echo "Please run kernelupdate.sh to download and update the kernel!"; exit;;
	esac
fi

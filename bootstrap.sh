#!/bin/bash

kernel_ver=`uname -r`
echo "Running kernel version: $kernel_ver"

if [ "$kernel_ver" != "5.2.0-mizar" ]; then
	echo "Mizar requires a patched kernel: 5.2.0-mizar for TCP to function correctly. Current version is $kernel_ver"

	read -p "Execute kernel update script (y/n)?" choice
	case "$choice" in
	  y|Y ) sh ./kernelpatch.sh;;
	  n|N ) echo "Please run kernelpatch.sh to download and update the kernel!"; exit;;
	  * ) echo "Please run kernelpatch.sh to download and update the kernel!"; exit;;
	esac
fi

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

ver=$(curl -s https://api.github.com/repos/kubernetes-sigs/kind/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
curl -Lo kind https://github.com/kubernetes-sigs/kind/releases/download/$ver/kind-$(uname)-amd64
chmod +x kind
mv kind /usr/local/bin

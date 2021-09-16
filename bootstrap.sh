#!/bin/bash

tput setaf 1
echo "NOTE: This script will reboot the system if you opt to allow kernel update."
echo "      If reboot is not required, it will log you out and require re-login for new permissions to take effect."
echo ""
read -n 1 -s -r -p "Press Ctrl-c to quit, any key to continue..."
tput sgr0

logout_needed=false

sudo apt-get update
sudo apt-get install -y \
    build-essential \
    clang-7 \
    llvm-7 \
    libelf-dev \
    python3.7 \
    python3-pip \
    libcmocka-dev \
    lcov \
    scapy \
    python3.7-dev \
    python3-apt \
    pkg-config \
    docker.io

sudo systemctl unmask docker.service
sudo systemctl unmask docker.socket

cat /etc/group | grep docker | grep ${USER} &> /dev/null
if [ $? -ne 0 ]; then
  sudo usermod -aG docker ${USER}
  logout_needed=true
fi

sudo systemctl start docker
sudo systemctl enable docker
# kopf no longer available in python3.6 via pip
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
sudo update-alternatives --set python3 /usr/bin/python3.7
# Fix for apt-pkg missing when using python3.7
sudo ln -s /usr/lib/python3/dist-packages/apt_pkg.cpython-36m-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/apt_pkg.so
sudo pip3 install setuptools netaddr docker grpcio grpcio-tools scapy kubernetes

ver=$(curl -s https://api.github.com/repos/kubernetes-sigs/kind/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
curl -Lo kind "https://github.com/kubernetes-sigs/kind/releases/download/$ver/kind-$(uname)-amd64"
chmod +x ./kind
sudo mv ./kind /usr/local/bin

curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

# Install kind
if [ ! -f /usr/local/bin/kind ]; then
    pushd /tmp
    ver=$(curl -s https://api.github.com/repos/kubernetes-sigs/kind/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")')
    curl -Lo kind "https://github.com/kubernetes-sigs/kind/releases/download/$ver/kind-$(uname)-amd64"
    chmod +x kind
    sudo mv kind /usr/local/bin
    popd
fi

git submodule update --init --recursive

kernel_ver=`uname -r`
kernel_header_ver=`sudo apt search linux-headers-$(uname -r)`

echo "Running kernel version: $kernel_ver"
echo ".................................................."
echo "Running kernel header version: $kernel_header_ver"

mj_ver=$(echo $kernel_ver | cut -d. -f1)
mn_ver=$(echo $kernel_ver | cut -d. -f2)
mj_header_ver=$(echo $kernel_header_ver | cut -d. -f7 | cut -d- -f3)
mn_header_ver=$(echo $kernel_header_ver | cut -d. -f8)

echo "$mj_ver"
echo "$mn_ver"
echo "$mj_header_ver"
echo "$mn_header_ver"

if ( [ "$mj_ver" -le 5 ] && [ "$mn_ver" -le 5 ] ) || ( [ "$mj_ver" -le 4 ] && [ "$mn_ver" -gt 5 ] ) ; then
    tput setaf 1
    echo "Mizar requires an updated kernel: linux-5.6 rc2 for TCP to function correctly. Current version is $kernel_ver"
    read -p "Execute kernel update script (y/n)?" choice
    tput sgr0
    case "$choice" in
      y|Y ) sh ./kernelupdate.sh;;
      n|N ) echo "Please run kernelupdate.sh to download and update the kernel!"; exit;;
      * ) echo "Please run kernelupdate.sh to download and update the kernel!"; exit;;
    esac
elif [[ "$mj_ver" != "$mj_header_ver" ]] || [[ "$mn_ver" != "$mn_header_ver" ]]; then
    tput setf 2
    echo " Update kernel_header..!! "
    tput sgr0
    sudo apt-get install linux-headers-$(uname -r)
fi

if [ "$logout_needed" = true ]; then
    logout
fi

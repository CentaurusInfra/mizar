#!/bin/bash

kernel_dir="../linux-5.6-rc2"
mkdir -p $kernel_dir

wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-headers-5.6.0-rc2_5.6.0-rc2-1_amd64.deb -P $kernel_dir
wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-image-5.6.0-rc2-dbg_5.6.0-rc2-1_amd64.deb -P $kernel_dir
wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-image-5.6.0-rc2_5.6.0-rc2-1_amd64.deb -P $kernel_dir
wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-libc-dev_5.6.0-rc2-1_amd64.deb -P $kernel_dir

read -p "Continue kernel update (y/n)?" choice
case "$choice" in
  y|Y ) echo "Updating kernel";;
  n|N ) exit;;
  * ) exit;;
esac

sudo dpkg -i $kernel_dir/*.deb

read -p "Reboot host (y/n)?" choice
case "$choice" in
  y|Y ) echo "Rebooting";;
  n|N ) exit;;
  * ) exit;;
esac

sudo reboot
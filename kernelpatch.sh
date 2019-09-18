#!/bin/bash

kernel_dir="../mizar-kernel"
mkdir -p $kernel_dir

wget https://mizar.s3.amazonaws.com/kernel/linux-headers-5.2.0-mizar_5.2.0-mizar-2_amd64.deb -P kernel_dir
wget https://mizar.s3.amazonaws.com/kernel/linux-image-5.2.0-mizar-dbg_5.2.0-mizar-2_amd64.deb -P $kernel_dir
wget https://mizar.s3.amazonaws.com/kernel/linux-image-5.2.0-mizar_5.2.0-mizar-2_amd64.deb -P $kernel_dir
wget https://mizar.s3.amazonaws.com/kernel/linux-libc-dev_5.2.0-mizar-2_amd64.deb -P $kernel_dir

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
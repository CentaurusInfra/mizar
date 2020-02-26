#!/bin/bash

kernel_ver=`nsenter -t 1 -m -u -n -i uname -r`
if [ "$kernel_ver" == "linux-5.6-rc2" ]; then
    echo 'mizar-complete'
else
    kernel_dir=~/linux-5.6-rc2
    nsenter -t 1 -m -u -n -i mkdir $kernel_dir

    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-headers-5.6.0-rc2_5.6.0-rc2-1_amd64.deb -P $kernel_dir
    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-image-5.6.0-rc2-dbg_5.6.0-rc2-1_amd64.deb -P $kernel_dir
    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-image-5.6.0-rc2_5.6.0-rc2-1_amd64.deb -P $kernel_dir
    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/linux-5.6-rc2/linux-libc-dev_5.6.0-rc2-1_amd64.deb -P $kernel_dir

    nsenter -t 1 -m -u -n -i dpkg --force-confnew -i $(nsenter -t 1 -m -u -n -i find $kernel_dir -name "*.deb") && nsenter -t 1 -m -u -n -i sudo reboot
fi
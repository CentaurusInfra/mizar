#!/bin/bash

kernel_ver=`nsenter -t 1 -m -u -n -i uname -r`
if [ "$kernel_ver" == "5.2.0-mizar" ]; then
    echo 'mizar-complete'
else
    kernel_dir=~/mizar-kernel
    nsenter -t 1 -m -u -n -i mkdir $kernel_dir

    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/kernel/linux-headers-5.2.0-mizar_5.2.0-mizar-2_amd64.deb -P $kernel_dir
    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/kernel/linux-image-5.2.0-mizar-dbg_5.2.0-mizar-2_amd64.deb -P $kernel_dir
    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/kernel/linux-image-5.2.0-mizar_5.2.0-mizar-2_amd64.deb -P $kernel_dir
    nsenter -t 1 -m -u -n -i wget https://mizar.s3.amazonaws.com/kernel/linux-libc-dev_5.2.0-mizar-2_amd64.deb -P $kernel_dir

    nsenter -t 1 -m -u -n -i dpkg --force-confnew -i $(nsenter -t 1 -m -u -n -i find $kernel_dir -name "*.deb") && nsenter -t 1 -m -u -n -i sudo reboot
fi

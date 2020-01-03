#!/bin/bash

rm -rf /home/ubuntu/mizar
git clone --recurse-submodules -j8 https://github.com/futurewei-cloud/mizar.git /home/ubuntu/mizar

make -C /home/ubuntu/mizar
make install -C /home/ubuntu/mizar

if [[ "$(docker images -q buildbox:v2 2> /dev/null)" == "" ]]; then
	echo "Building docker image"
	sudo docker build -f /home/ubuntu/mizar/scripts/Dockerfile -t buildbox:v2 /home/ubuntu/mizar/scripts
fi

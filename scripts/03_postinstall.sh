#!/bin/bash

if [[ "$(docker images -q buildbox:v2 2> /dev/null)" == "" ]]; then
	echo "Building docker image"
	sudo docker build -f /home/ubuntu/mizar/scripts/Dockerfile -t buildbox:v2 /home/ubuntu/mizar/scripts
fi

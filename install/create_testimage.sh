#!/bin/bash

DIR=${1:-.}
USER=${2:-user}
DOCKER_ACC=${3:-"localhost:5000"}

# Build the daemon image
docker image build -t $DOCKER_ACC/testpod:latest -f $DIR/mgmt/etc/docker/test.Dockerfile $DIR
docker image push $DOCKER_ACC/testpod:latest
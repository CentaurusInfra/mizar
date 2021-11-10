#!/bin/bash
DIR=${1:-.}
DOCKER_ACC=${2:-"yangpengzx"}
VERSION=${3:-"0.92"}

docker image build -t $DOCKER_ACC/dropletd_ustc:$VERSION -f $DIR/etc/docker/daemon_ustc.Dockerfile $DIR
docker image push $DOCKER_ACC/dropletd_ustc:$VERSION

docker image build -t $DOCKER_ACC/mizar:$VERSION -f $DIR/etc/docker/mizar.Dockerfile $DIR
docker image push $DOCKER_ACC/mizar:$VERSION
#!/bin/bash

DIR=${1:-.}
USER=${2:-dev}
DOCKER_ACC=${3:-"localhost:5000"}
YAML_FILE="dev.daemon.deploy.yaml"

if [[ "$USER" == "user" || "$USER" == "final" ]]; then
    DOCKER_ACC="fwnetworking"
    YAML_FILE="daemon.deploy.yaml"
fi

# Build the daemon image
docker image build -t $DOCKER_ACC/dropletd:latest -f $DIR/mgmt/etc/docker/daemon.Dockerfile $DIR
if [[ "$USER" == "dev" || "$USER" == "final" ]]; then
    docker image push $DOCKER_ACC/dropletd:latest
fi

# Delete existing deployment and deploy
kubectl delete daemonset.apps/mizar-daemon 2> /tmp/kubetctl.err
kubectl apply -f $DIR/mgmt/etc/deploy/$YAML_FILE

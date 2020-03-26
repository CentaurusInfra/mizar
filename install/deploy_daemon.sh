#!/bin/bash

DIR=${1:-.}
USER=${2:-user}
DOCKER_ACC=${3:-fwnetworking}

# Build the daemon image
if [[ "$USER" == "dev" ]]; then
    docker image build -t $DOCKER_ACC/dropletd:latest -f $DIR/mgmt/etc/docker/daemon.Dockerfile $DIR
    docker image push $DOCKER_ACC/dropletd:latest
fi

# Delete existing deployment and deploy
kubectl delete daemonset.apps/mizar-daemon
kubectl apply -f $DIR/mgmt/etc/deploy/daemon.deploy.yaml

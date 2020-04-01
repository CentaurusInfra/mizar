#!/bin/bash

DIR=${1:-.}
USER=${2:-dev}
DOCKER_ACC=${3:-"localhost:5000"}
YAML_FILE="daemon.deploy.yaml"

# Build the daemon image
docker image build -t $DOCKER_ACC/dropletd:latest -f $DIR/mgmt/etc/docker/daemon.Dockerfile $DIR
if [[ "$USER" == "dev" || "$USER" == "final" ]]; then
    docker image push $DOCKER_ACC/dropletd:latest
fi

if [[ "$USER" == "dev" ]]; then
    YAML_FILE="dev.daemon.deploy.yaml"
fi

# Delete existing deployment and deploy
kubectl delete daemonset.apps/mizar-daemon 2> /tmp/kubetctl.err
kubectl apply -f $DIR/mgmt/etc/deploy/$YAML_FILE

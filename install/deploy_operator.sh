#!/bin/bash

DIR=${1:-.}
USER=${2:-dev}
DOCKER_ACC=${3:-"localhost:5000"}
YAML_FILE="dev.operator.deploy.yaml"

if [[ "$USER" == "user" || "$USER" == "final" ]]; then
    DOCKER_ACC="fwnetworking"
    YAML_FILE="operator.deploy.yaml"
fi

# Build the operator image
docker image build -t $DOCKER_ACC/endpointopr:latest -f $DIR/mgmt/etc/docker/operator.Dockerfile $DIR
if [[ "$USER" == "dev" || "$USER" == "final" ]]; then
    docker image push $DOCKER_ACC/endpointopr:latest
fi

# Delete existing deployment and deploy
kubectl delete deployment.apps/mizar-operator 2> /tmp/kubetctl.err
kubectl apply -f $DIR/mgmt/etc/deploy/$YAML_FILE

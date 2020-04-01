#!/bin/bash

DIR=${1:-.}
USER=${2:-user}
DOCKER_ACC=${3:-"localhost:5000"}
YAML_FILE="operator.deploy.yaml"

# Build the operator image
docker image build -t $DOCKER_ACC/endpointopr:latest -f $DIR/mgmt/etc/docker/operator.Dockerfile $DIR
if [[ "$USER" == "dev" || "$USER" == "final" ]]; then
    docker image push $DOCKER_ACC/endpointopr:latest
fi

if [[ "$USER" == "dev" ]]; then
    YAML_FILE="dev.operator.deploy.yaml"
fi

# Delete existing deployment and deploy
kubectl delete deployment.apps/mizar-operator 2> /dev/null
kubectl apply -f $DIR/mgmt/etc/deploy/$YAML_FILE

#!/bin/bash

DIR=${1:-.}
USER=${2:-user}
DOCKER_ACC=${3:-fwnetworking}

# Build the operator image
docker image build -t $DOCKER_ACC/endpointopr:latest -f $DIR/mgmt/etc/docker/operator.Dockerfile $DIR
if [[ "$USER" == "dev" ]]; then
    docker image push $DOCKER_ACC/endpointopr:latest
fi

# Delete existing deployment and deploy
kubectl delete deployment.apps/mizar-operator
kubectl apply -f $DIR/mgmt/etc/deploy/operator.deploy.yaml

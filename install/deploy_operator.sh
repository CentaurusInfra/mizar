#!/bin/bash

DIR=${1:-.}

# Build the operator image
docker image build -t phudtran/endpointopr:latest -f $DIR/mgmt/etc/docker/operator.Dockerfile $DIR
docker image push phudtran/endpointopr:latest

# Delete existing deployment and deploy
kubectl delete deployment.apps/mizar-operator
kubectl apply -f $DIR/mgmt/etc/deploy/operator.deploy.yaml

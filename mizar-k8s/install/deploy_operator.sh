#!/bin/bash

DIR=${1:-.}
DIR="${DIR}/mizar-k8s"

# Delete existing deployment
kubectl delete daemonset.apps/mizar-dropletd
kubectl delete deployment.apps/mizar-operator

# Deploy the mizar operator and dropletd
kubectl apply -f $DIR/deployments/droplet.deploy.yaml
kubectl apply -f $DIR/deployments/operator.deploy.yaml


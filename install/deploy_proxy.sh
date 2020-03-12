#!/bin/bash

DIR=${1:-.}

# Build the proxyopr image
docker image build -t phudtran/proxyopr:latest -f $DIR/mgmt/etc/docker/proxy.Dockerfile $DIR
docker image push phudtran/proxyopr:latest

# Delete existing deployment and deploy
kubectl delete deployment.apps/mizar-proxyopr
kubectl apply -f $DIR/mgmt/etc/deploy/proxy.deploy.yaml

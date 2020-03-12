#!/bin/bash

DIR=${1:-.}

# Build the daemon image
docker image build -t phudtran/dropletd:latest -f $DIR/mgmt/etc/docker/daemon.Dockerfile $DIR
docker image push phudtran/dropletd:latest

# Delete existing deployment and deploy
kubectl delete daemonset.apps/mizar-daemon
kubectl apply -f $DIR/mgmt/etc/deploy/daemon.deploy.yaml

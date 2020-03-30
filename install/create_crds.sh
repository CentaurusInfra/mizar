#!/bin/bash

DIR=${1:-.}
USER=${2:-user}

# Create the CRDs
kubectl delete bouncers.mizar.com --all
kubectl delete dividers.mizar.com --all
kubectl delete droplets.mizar.com --all
kubectl delete endpoints.mizar.com --all
kubectl delete nets.mizar.com --all
kubectl delete vpcs.mizar.com --all

kubectl apply -f $DIR/mgmt/etc/crds/bouncers.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/dividers.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/droplets.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/endpoints.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/nets.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/vpcs.crd.yaml

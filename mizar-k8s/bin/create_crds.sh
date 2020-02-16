#!/bin/bash

DIR=${1:-.}

# Create the CRDs
kubectl delete endpoints.mizar.com --all
kubectl delete droplets.mizar.com --all
kubectl apply -f $DIR/crds/droplets.crd.yaml
kubectl apply -f $DIR/crds/endpoints.crd.yaml
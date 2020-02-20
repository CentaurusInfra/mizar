#!/bin/bash

DIR=${1:-.}

# Create the CRDs
kubectl delete bouncers.mizar.com --all
kubectl delete dividers.mizar.com --all
kubectl delete droplets.mizar.com --all
kubectl delete endpoints.mizar.com --all
kubectl delete nets.mizar.com --all
kubectl delete vpcs.mizar.com --all

kubectl apply -f $DIR/crds/bouncers.crd.yaml
kubectl apply -f $DIR/crds/dividers.crd.yaml
kubectl apply -f $DIR/crds/droplets.crd.yaml
kubectl apply -f $DIR/crds/endpoints.crd.yaml
kubectl apply -f $DIR/crds/nets.crd.yaml
kubectl apply -f $DIR/crds/vpcs.crd.yaml

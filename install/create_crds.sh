#!/bin/bash

DIR=${1:-.}
USER=${2:-dev}

# Create the CRDs
kubectl delete bouncers.mizar.com --all 2> /tmp/kubetctl.err
kubectl delete dividers.mizar.com --all 2> /tmp/kubetctl.err
kubectl delete droplets.mizar.com --all 2> /tmp/kubetctl.err
kubectl delete endpoints.mizar.com --all 2> /tmp/kubetctl.err
kubectl delete nets.mizar.com --all 2> /tmp/kubetctl.err
kubectl delete vpcs.mizar.com --all 2> /tmp/kubetctl.err

kubectl apply -f $DIR/mgmt/etc/crds/bouncers.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/dividers.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/droplets.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/endpoints.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/nets.crd.yaml
kubectl apply -f $DIR/mgmt/etc/crds/vpcs.crd.yaml

#!/bin/bash

DIR=${1:-.}

# Create the service account
kubectl apply -f $DIR/etc/serviceaccount.yaml

# Bind the service account to cluster admin
kubectl apply -f $DIR/etc/binding.yaml
#!/bin/bash

DIR=${1:-.}
DIR="${DIR}/mizar-k8s"

# Build the operator image
docker image build -t selgohari/endpointopr:latest -f $DIR/images/operator.Dockerfile $1
docker image push selgohari/endpointopr:latest

# Build the droplet image
docker image build -t selgohari/dropletd:latest -f $DIR/images/droplet.Dockerfile $1
docker image push selgohari/dropletd:latest
#!/bin/bash

DIR=${1:-.}

# Build the daemon image
docker image build -t phudtran/testpod:latest -f $DIR/mgmt/etc/docker/test.Dockerfile $DIR
docker image push phudtran/testpod:latest
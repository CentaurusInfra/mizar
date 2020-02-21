#!/bin/bash

DIR=${1:-.}
DIR="${DIR}/mizar-k8s"

# Installing mizar cni
api_ip=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kind-control-plane`
sed "s/server: https:\/\/127.0.0.1:[[:digit:]]\+/server: https:\/\/$api_ip:6443/" ~/.kube/config > /tmp/config
docker cp /tmp/config kind-control-plane:/etc/mizarcni.config
docker cp $DIR/cni/10-mizarcni.conf kind-control-plane:/etc/cni/net.d/10-mizarcni.conf
docker cp $DIR/cni/mizarcni.py kind-control-plane:/opt/cni/bin/mizarcni.py

# Removing exisiting kind CNI
docker exec kind-control-plane rm /etc/cni/net.d/10-kindnet.conflist

# Kind image
docker exec kind-control-plane apt update
docker exec kind-control-plane apt install -y python3
docker exec kind-control-plane apt install -y python3-pip
docker exec kind-control-plane pip3 install kubernetes
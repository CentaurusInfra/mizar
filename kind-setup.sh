#!/bin/bash

CWD=$(pwd)
KINDCONF="${HOME}/mizar/build/tests/kind/config"
MIZARCONF="${HOME}/mizar/build/tests/mizarcni.config"
KINDHOME="${HOME}/.kube/config"

kind delete cluster

docker image build -t phudtran/kindnode:latest -f k8s/kind/Dockerfile .

kind create cluster --config k8s/kind/cluster.yaml --kubeconfig $KINDCONF

api_ip=`docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' kind-control-plane`
sed "s/server: https:\/\/127.0.0.1:[[:digit:]]\+/server: https:\/\/$api_ip:6443/" $KINDCONF > $MIZARCONF
ln -snf $KINDCONF $KINDHOME

source install/create_crds.sh $CWD
source install/create_service_account.sh $CWD

source install/deploy_daemon.sh $CWD
source install/deploy_operator.sh $CWD
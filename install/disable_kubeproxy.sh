#!/bin/bash

DIR=${1:-.}
USER=${2:-user}

kubectl delete daemonsets -n kube-system kube-proxy

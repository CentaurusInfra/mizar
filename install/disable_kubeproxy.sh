#!/bin/bash

DIR=${1:-.}
USER=${2:-dev}

kubectl delete daemonsets -n kube-system kube-proxy

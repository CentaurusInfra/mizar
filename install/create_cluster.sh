#!/bin/bash

KINDCONF=${1:-"${HOME}/mizar/build/tests/kind/config"}
USER=${2:-user}

# create registry container unless it already exists
reg_name='local-kind-registry'
reg_port='5000'
running="$(docker inspect -f '{{.State.Running}}' "${reg_name}" 2>/dev/null || true)"
if [ "${running}" != 'true' ]; then
  docker run \
    -d --restart=always -p "${reg_port}:5000" --name "${reg_name}" \
    registry:2
fi
reg_ip="$(docker inspect -f '{{.NetworkSettings.IPAddress}}' "${reg_name}")"

if [[ $USER == "dev" ]]; then
  PATCH="containerdConfigPatches:
- |-
  [plugins.\"io.containerd.grpc.v1.cri\".registry.mirrors.\"localhost:${reg_port}\"]
    endpoint = [\"http://${reg_ip}:${reg_port}\"]"
  REPO="localhost:5000"
else
  PATCH=""
  REPO="fwnetworking"
fi

# create a cluster with the local registry enabled in containerd
cat <<EOF | kind create cluster --name kind --kubeconfig ${KINDCONF} --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
${PATCH}
nodes:
  - role: control-plane
    image: ${REPO}/kindnode:latest
    extraMounts:
      - hostPath: .
        containerPath: /var/mizar
  - role: worker
    image: ${REPO}/kindnode:latest
    extraMounts:
      - hostPath: .
        containerPath: /var/mizar
  - role: worker
    image: ${REPO}/kindnode:latest
    extraMounts:
      - hostPath: .
        containerPath: /var/mizar
  - role: worker
    image: ${REPO}/kindnode:latest
    extraMounts:
      - hostPath: .
        containerPath: /var/mizar
  - role: worker
    image: ${REPO}/kindnode:latest
    extraMounts:
      - hostPath: .
        containerPath: /var/mizar
EOF
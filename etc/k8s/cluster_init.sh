#!/bin/bash

set -euo pipefail

function main() {
    timeout=600

    # Initial setup for all nodes.
    run_job kernelpatch-node-daemonset.yaml kernelpatch-node $timeout
    run_job node-init-daemonset.yaml node-init $timeout
    # Start transitd on all nodes.
    kubectl apply -f transitd-daemonset.yaml
    check_status "running" transitd-daemonset.yaml transitd $timeout
    # Load transit xdp program on main interface of all nodes.
    run_job load-transit-xdp-daemonset.yaml load-transit-xdp $timeout
}

function run_job() {
    running="running"
    done="done"
    yaml_file=$1
    pod_name=$2
    timeout=$3

    kubectl apply -f $yaml_file
    check_status $running $yaml_file $pod_name $timeout
    check_status $done $yaml_file $pod_name $timeout
    kubectl delete -f $yaml_file
}

function check_status() {
    status=$1
    yaml_file=$2
    pod_name=$3
    timeout=$4

    pods=$(kubectl get pods | grep $pod_name | awk '{print $1}')
    end=$((SECONDS+$timeout))

    for pod in ${pods}; do
        echo -n "Waiting for pod:$pod"
        while [[ $SECONDS -lt $end ]]; do
            # We can add a "case" statement here for more status checks in the future.
            if [[ $status == "running" ]]; then
                check_running $pod || break
            else
                check_done $pod || break
            fi
        done
        echo
        if [[ $SECONDS -lt $end ]]; then
            echo "Pod:${pod} now $status!"
        else
            echo "ERROR: ${pod} timed out after $timeout seconds!"
            kubectl delete -f $yaml_file
            exit 1
        fi
    done

    echo
    echo "All $pod_name pods now $status!"
    echo
}

function check_done() {
    pod=$1
    if [[ $(kubectl logs $pod --tail 1) == "mizar-complete" ]]; then
        return 1
    else
        sleep 2
        echo -n "."
        return 0
    fi
}

function check_running() {
    pod=$1
    if [[ $(kubectl get pod $pod -o go-template --template "{{.status.phase}}") == "Running" ]]; then
        return 1
    else
        sleep 2
        echo -n "."
        return 0
    fi
}

main

  
FROM golang:1.14 as clone
WORKDIR /
RUN git clone --branch v0.17.0 https://github.com/kubernetes/code-generator

# Generate code based on the input Go code.
FROM golang:1.14 as generatecode
COPY --from=clone /code-generator /code-generator/
COPY ./ /crds-operators/vpcs
WORKDIR /code-generator
RUN go mod edit -replace=mizar.futurewei.com/crds-operators/vpcs=../crds-operators/vpcs
RUN ./generate-groups.sh all mizar.futurewei.com/crds-operators/vpcs/apis/generated mizar.futurewei.com/crds-operators/vpcs apis:v1 --go-header-file ./hack/boilerplate.go.txt --output-base ..
RUN cp -r /mizar.futurewei.com/crds-operators/vpcs/apis/* /crds-operators/vpcs/apis/

# Run custom resource controller. Requires KUBECONFIG env and a running Kubernetes cluster.
FROM golang:1.14
COPY --from=generatecode /crds-operators/vpcs /crds-operators/vpcs
WORKDIR /crds-operators/vpcs/cmd/controller
ENTRYPOINT [ "go", "run", "." ]

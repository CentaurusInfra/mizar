#gRPC 
FROM golang:1.14 as server
WORKDIR /
#Protoc plugin install
RUN go get github.com/golang/protobuf/protoc-gen-go
ENV PATH="${PATH}:$(go env GOPATH)/bin" 
#protobuf compiler install
RUN PB_REL="https://github.com/protocolbuffers/protobuf/releases"
RUN curl -LO https://github.com/protocolbuffers/protobuf/releases/download/v3.12.1/protoc-3.12.1-linux-x86_64.zip
RUN \
apt-get update && \
apt-get install unzip
RUN unzip protoc-3.12.1-linux-x86_64.zip -d $HOME/.local
ENV PATH="$HOME/.local/bin:${PATH}"
RUN export PATH="$PATH:$HOME/.local/bin"
#grpc-go install 
WORKDIR /crds-operator-proxy
RUN git clone -b v1.30.0 https://github.com/grpc/grpc-go
WORKDIR /crds-operator-proxy/grpc
COPY . /crds-operator-proxy/grpc
RUN (cd ../grpc-go/cmd/protoc-gen-go-grpc && go install .)
RUN ls $HOME/.local/bin
ENV PATH=${PATH}:${HOME}/.local/bin
RUN $HOME/.local/bin/protoc \
  --go_out=Mgrpc/service_config/service_config.proto=/internal/proto/grpc_service_config:. \
  --go-grpc_out=Mgrpc/service_config/service_config.proto=/internal/proto/grpc_service_config:. \
  --go_opt=paths=source_relative \
  --go-grpc_opt=paths=source_relative \
  vpcs/vpcs.proto

RUN pwd
RUN ls -al /
EXPOSE 50051
#CMD go run ./Vpcs_server/main.go
ENTRYPOINT [ "go", "run", "." ]

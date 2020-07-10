all: container

VERSION = 0.1
TAG = $(VERSION)
PREFIX = crd/velotio-blog

DOCKER_RUN = docker run --rm -v $(shell pwd)/../:/go/src/blog.velotio.com/ -w /go/src/blog.velotio.com/crd-example/
	GOLANG_CONTAINER = golang:1.8
	DOCKERFILE = Dockerfile

BUILD_IN_CONTAINER = 1

crd-blog:
ifeq ($(BUILD_IN_CONTAINER),1)
	        $(DOCKER_RUN) -e CGO_ENABLED=0 $(GOLANG_CONTAINER) go build -a -installsuffix cgo -ldflags "-w -X main.version=${VERSION}" -o crd-blog *.go
else
	        CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags "-w -X main.version=${VERSION}" -o crd-blog *.go
endif

container: crd-blog
	docker build -f $(DOCKERFILE) -t $(PREFIX):$(TAG) .
	rm -f crd-blog



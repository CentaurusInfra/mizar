module := mizar

submodules := tests
-include $(patsubst %, $(module)/%/module.mk, $(submodules))

GRPC_FLAGS := -I mizar/proto/ --python_out=. --grpc_python_out=.

PATH := $(PATH):/usr/local/go/bin:$(HOME)/go/bin

.PHONY: proto
proto:
	python3 -m grpc_tools.protoc $(GRPC_FLAGS) mizar/proto/mizar/proto/*.proto
	whereis protoc
	whereis protoc-gen-go
	printenv
	echo /usr/bin/protoc
	ls /usr/bin/protoc
	echo $(HOME)/go/bin
	ls $(HOME)/go/bin
	protoc --go_out=. --go-grpc_out=. mizar/proto/mizar/proto/interface.proto

clean::
	rm -rf mizar/proto/__pycache__
	find mizar/proto/ -name '*.py' -not -name '__init__.py' -delete
	find mizarcni/main/ -name '*.pb.go' -delete
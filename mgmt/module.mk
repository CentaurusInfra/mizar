module := mgmt

submodules := tests
-include $(patsubst %, $(module)/%/module.mk, $(submodules))

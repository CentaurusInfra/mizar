module := mizar

submodules := tests
-include $(patsubst %, $(module)/%/module.mk, $(submodules))

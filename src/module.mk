# SPDX-License-Identifier: GPL-2.0-or-later

module := src
submodules := rpcgen cli extern dmn xdp
-include $(patsubst %, $(module)/%/module.mk, $(submodules))

CFLAGS += -Isrc -Isrc/include
CLANGFLAGS += -Isrc -Isrc/include
CLANGFLAGS_DEBUG += -Isrc -Isrc/include

all:: $(submodules)

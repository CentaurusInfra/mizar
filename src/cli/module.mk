# SPDX-License-Identifier: GPL-2.0-or-later

clisrc = $(wildcard src/cli/*.c)
cliobj = $(clisrc:.c=.o)

CFLAGS += -fprofile-arcs -ftest-coverage


cli: $(cliobj) $(rpcgen_clnt_obj) src/extern/cJSON.o
	$(CC) -o build/bin/transit $^ $(LDFLAGS) $(CFLAGS)

clean::
	rm -f src/cli/*.o
	rm -f src/cli/*.gcno
	rm -f src/cli/*.gcda
	rm -f build/bin/transit

include src/cli/test/module.mk

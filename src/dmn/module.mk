# SPDX-License-Identifier: GPL-2.0-or-later

dmnsrc = $(wildcard src/dmn/*.c)
dmnobj = $(dmnsrc:.c=.o)

CFLAGS += -fprofile-arcs -ftest-coverage

dmn: $(dmnobj) $(rpcgen_svc_obj)
	$(CC) -o build/bin/transitd $^ $(LDFLAGS) $(CFLAGS)

clean::
	rm -f src/dmn/*.o
	rm -f src/dmn/*.gcno
	rm -f src/dmn/*.gcda
	rm -f build/bin/transitd

include src/dmn/test/module.mk

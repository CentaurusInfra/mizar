# SPDX-License-Identifier: GPL-2.0-or-later

xdpsrc = $(wildcard src/xdp/*.c)
xdpobj = $(xdpsrc:.c=_ebpf.o)
xdptestobj = $(xdpsrc:.c=_ebpf_debug.o)

.PHONY: xdp
xdp: $(xdpobj) $(xdptestobj)

%_ebpf.o: %.c
	$(CLANG) -c $^ $(CLANGFLAGS) | $(LLC)  -o $@
	cp $@ build/xdp

%_ebpf_debug.o: %.c
	$(CLANG) -c $^ $(CLANGFLAGS_DEBUG) | $(LLC)  -o $@
	cp $@ build/xdp

clean::
	rm -f src/xdp/*.o
	rm -f build/xdp/*

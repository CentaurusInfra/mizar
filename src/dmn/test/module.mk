# SPDX-License-Identifier: GPL-2.0-or-later

dmntestsrc = $(wildcard src/dmn/test/*.c)
dmntestsrc += $(filter-out src/dmn/trn_transitd.c, $(dmnsrc))
dmntestobj = $(dmntestsrc:.c=.o)

CFLAGS += -fprofile-arcs -ftest-coverage
LDFLAGS += -lcmocka

unittest:: test_dmn

CLI_MOCKS += -Wl,--wrap=bpf_map_update_elem
CLI_MOCKS += -Wl,--wrap=bpf_map_lookup_elem
CLI_MOCKS += -Wl,--wrap=bpf_prog_load_xattr
CLI_MOCKS += -Wl,--wrap=bpf_set_link_xdp_fd
CLI_MOCKS += -Wl,--wrap=bpf_obj_get_info_by_fd
CLI_MOCKS += -Wl,--wrap=bpf_map__next
CLI_MOCKS += -Wl,--wrap=bpf_map__fd
CLI_MOCKS += -Wl,--wrap=bpf_map__pin
CLI_MOCKS += -Wl,--wrap=bpf_map__unpin
CLI_MOCKS += -Wl,--wrap=bpf_get_link_xdp_id
CLI_MOCKS += -Wl,--wrap=if_nametoindex
CLI_MOCKS += -Wl,--wrap=if_indextoname


test_dmn: $(dmntestobj) $(rpcgen_svc_obj)
	$(CC) -o build/tests/$@ $^ $(LDFLAGS) $(CLI_MOCKS) $(CFLAGS)

clean::
	rm -f src/dmn/test/*.o
	rm -f src/dmn/test/*.gcno
	rm -f src/dmn/test/*.gcda
	rm -f build/tests/test_dmn


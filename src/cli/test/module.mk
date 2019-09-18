# SPDX-License-Identifier: GPL-2.0-or-later

clitestsrc = $(wildcard src/cli/test/*.c)
clitestsrc += $(filter-out src/cli/trn_cli.c, $(clisrc))
clitestobj = $(clitestsrc:.c=.o)

CFLAGS += -fprofile-arcs -ftest-coverage
LDFLAGS += -lcmocka

# Mocked symbols
CLI_MOCKS += -Wl,--wrap=update_vpc_1
CLI_MOCKS += -Wl,--wrap=update_net_1
CLI_MOCKS += -Wl,--wrap=update_ep_1
CLI_MOCKS += -Wl,--wrap=update_agent_ep_1
CLI_MOCKS += -Wl,--wrap=update_agent_md_1
CLI_MOCKS += -Wl,--wrap=load_transit_xdp_1
CLI_MOCKS += -Wl,--wrap=unload_transit_xdp_1
CLI_MOCKS += -Wl,--wrap=load_transit_agent_xdp_1
CLI_MOCKS += -Wl,--wrap=unload_transit_agent_xdp_1
CLI_MOCKS += -Wl,--wrap=get_vpc_1
CLI_MOCKS += -Wl,--wrap=get_net_1
CLI_MOCKS += -Wl,--wrap=get_ep_1
CLI_MOCKS += -Wl,--wrap=get_agent_ep_1
CLI_MOCKS += -Wl,--wrap=get_agent_md_1


unittest:: test_cli

test_cli: $(clitestobj) $(rpcgen_clnt_obj) src/extern/cJSON.o
	$(CC) -o build/tests/$@ $^ $(LDFLAGS) $(CLI_MOCKS) $(CFLAGS)

clean::
	rm -f src/cli/test/*.o
	rm -f src/cli/test/*.gcno
	rm -f src/cli/test/*.gcda
	rm -f build/tests/test_cli


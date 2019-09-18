# SPDX-License-Identifier: GPL-2.0-or-later

dir = src/rpcgen

protocol.x = $(dir)/trn_rpc_protocol.x

rpcgen_svc_src.c = $(dir)/trn_rpc_protocol_svc.c
rpcgen_clnt_src.c = $(dir)/trn_rpc_protocol_clnt.c
rpcgen_hdr.h = $(dir)/trn_rpc_protocol.h
rpcgen_xdr_src.c = $(dir)/trn_rpc_protocol_xdr.c
rpcgen_targets = $(rpcgen_xdr_src.c) $(rpcgen_hdr.h) $(rpcgen_clnt_src.c) $(rpcgen_svc_src.c)

rpcgen_clnt_obj = $(rpcgen_clnt_src.c:%.c=%.o) $(rpcgen_xdr_src.c:%.c=%.o)
rpcgen_svc_obj = $(rpcgen_svc_src.c:%.c=%.o) $(rpcgen_xdr_src.c:%.c=%.o)

LDLIBS += -lnsl
RPCGENFLAGS = -L -C

.PHONY: rpcgen
rpcgen: $(rpcgen_targets)

$(rpcgen_hdr.h): $(protocol.x)
	rm -f $(dir)/trn_rpc_protocol.h && rpcgen -h $(RPCGENFLAGS) $(protocol.x) -o $(dir)/trn_rpc_protocol.h

$(rpcgen_svc_src.c): $(protocol.x)
	rm -f $(dir)/trn_rpc_protocol_svc.c &&rpcgen -m $(RPCGENFLAGS) $(protocol.x) -o $(dir)/trn_rpc_protocol_svc.c

$(rpcgen_clnt_src.c): $(protocol.x)
	rm -f $(dir)/trn_rpc_protocol_clnt.c && rpcgen -l $(RPCGENFLAGS) $(protocol.x) -o $(dir)/trn_rpc_protocol_clnt.c

$(rpcgen_xdr_src.c): $(protocol.x)
	rm -f $(dir)/trn_rpc_protocol_xdr.c && rpcgen -c $(RPCGENFLAGS) $(protocol.x) -o $(dir)/trn_rpc_protocol_xdr.c

$(rpcgen_clnt_obj) : $(rpcgen_hdr.h) $(rpcgen_clnt_src.c) $(rpcgen_xdr_src.c)

$(rpcgen_svc_obj) : $(rpcgen_hdr.h) $(rpcgen_svc_src.c) $(rpcgen_xdr_src.c)

clean::
	$(RM) $(dir)/*.h $(dir)/*.c $(dir)/*.stub $(dir)/Makefile* $(dir)/*.o $(dir)/*.gcno $(dir)/*.gcda


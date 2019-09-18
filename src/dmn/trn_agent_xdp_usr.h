// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_agent_xdp_usr.h
 * @author Sherif Abdelwahab (@zasherif)
 * @       Phu Tran          (@phudtran)
 *
 * @brief User space APIs and data structures to program transit
 * agent.
 *
 * @copyright Copyright (c) 2019 The Authors.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 */
#pragma once

#include <argp.h>
#include <arpa/inet.h>
#include <assert.h>
#include <errno.h>
#include <libgen.h>
#include <linux/bpf.h>
#include <linux/if_link.h>
#include <net/if.h>
#include <netinet/in.h>
#include <search.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <unistd.h>

#include "bpf/bpf.h"
#include "bpf/libbpf.h"

#include "extern/cJSON.h"

#include "trn_datamodel.h"

struct agent_user_metadata_t {
	int ifindex;
	int prog_fd;
	int tunifindex;

	__u32 xdp_flags;
	__u32 prog_id;
	char pcapfile[256];

	int jump_table_fd;
	int agentmetadata_map_fd;
	int endpoints_map_fd;

	struct bpf_map *jmp_table;
	struct bpf_map *agentmetadata_map;
	struct bpf_map *endpoints_map;
	struct bpf_map *xdpcap_hook_map;

	struct bpf_prog_info info;
	struct bpf_object *obj;
};

int trn_agent_user_metadata_free(struct agent_user_metadata_t *md);

int trn_agent_update_agent_metadata(struct agent_user_metadata_t *umd,
				    struct agent_metadata_t *md);

int trn_agent_get_agent_metadata(struct agent_user_metadata_t *umd,
				 struct agent_metadata_t *md);

int trn_agent_update_endpoint(struct agent_user_metadata_t *umd,
			      struct endpoint_key_t *epkey,
			      struct endpoint_t *ep);

int trn_agent_get_endpoint(struct agent_user_metadata_t *umd,
			   struct endpoint_key_t *epkey, struct endpoint_t *ep);

int trn_agent_bpf_maps_init(struct agent_user_metadata_t *md);

int trn_agent_metadata_init(struct agent_user_metadata_t *md, char *itf,
			    char *agent_kern_path, int xdp_flags);

int trn_agent_add_prog(struct agent_user_metadata_t *umd, int prog,
		       int prog_fd);

// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_agent_xdp_usr.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief User space APIs to program transit agent
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
#include "trn_agent_xdp_usr.h"
#include "trn_log.h"

int trn_agent_user_metadata_free(struct agent_user_metadata_t *md)
{
	__u32 curr_prog_id = 0;

	if (bpf_map__unpin(md->xdpcap_hook_map, md->pcapfile)) {
		TRN_LOG_ERROR("Failed to unpin the pcap map file.");
		return 1;
	}

	if (bpf_get_link_xdp_id(md->ifindex, &curr_prog_id, md->xdp_flags)) {
		TRN_LOG_ERROR("bpf_get_link_xdp_id failed.");
		return 1;
	}

	if (md->prog_id == curr_prog_id)
		bpf_set_link_xdp_fd(md->ifindex, -1, md->xdp_flags);
	else if (!curr_prog_id)
		TRN_LOG_WARN("Couldn't find a prog id on a given interface.");
	else
		TRN_LOG_WARN("program on interface changed, not removing.");

	return 0;
}

int trn_agent_update_agent_metadata(struct agent_user_metadata_t *umd,
				    struct agent_metadata_t *md)
{
	int key = 0;
	int err = bpf_map_update_elem(umd->agentmetadata_map_fd, &key, md, 0);
	if (err) {
		TRN_LOG_ERROR("Configuring agent metadata (err:%d).", err);
		return 1;
	}

	return 0;
}

int trn_agent_get_agent_metadata(struct agent_user_metadata_t *umd,
				 struct agent_metadata_t *md)
{
	int key = 0;
	int err = bpf_map_lookup_elem(umd->agentmetadata_map_fd, &key, md);
	if (err) {
		TRN_LOG_ERROR("Querying agent metadata (err:%d).", err);
		return 1;
	}

	return 0;
}

int trn_agent_add_prog(struct agent_user_metadata_t *umd, int prog, int prog_fd)
{
	int err = bpf_map_update_elem(umd->jump_table_fd, &prog, &prog_fd, 0);
	if (err) {
		TRN_LOG_ERROR("Configuring agent metadata (err:%d).", err);
		return 1;
	}
	return 0;
}

int trn_agent_update_endpoint(struct agent_user_metadata_t *umd,
			      struct endpoint_key_t *epkey,
			      struct endpoint_t *ep)
{
	int err = bpf_map_update_elem(umd->endpoints_map_fd, epkey, ep, 0);
	if (err) {
		TRN_LOG_ERROR("Store endpoint mapping failed (err:%d).", err);
		return 1;
	}
	return 0;
}

int trn_agent_get_endpoint(struct agent_user_metadata_t *umd,
			   struct endpoint_key_t *epkey, struct endpoint_t *ep)
{
	int err = bpf_map_lookup_elem(umd->endpoints_map_fd, epkey, ep);
	if (err) {
		TRN_LOG_ERROR(
			"Querying agent endpoint mapping failed (err:%d).",
			err);
		return 1;
	}
	return 0;
}

int trn_agent_bpf_maps_init(struct agent_user_metadata_t *md)
{
	md->jmp_table = bpf_map__next(NULL, md->obj);
	md->agentmetadata_map = bpf_map__next(md->jmp_table, md->obj);
	md->endpoints_map = bpf_map__next(md->agentmetadata_map, md->obj);
	md->xdpcap_hook_map = bpf_map__next(md->endpoints_map, md->obj);

	if (!md->jmp_table || !md->agentmetadata_map ||
	    !md->endpoints_map | !md->xdpcap_hook_map) {
		TRN_LOG_ERROR("Failure finding maps objects.");
		return 1;
	}

	md->jump_table_fd = bpf_map__fd(md->jmp_table);
	md->agentmetadata_map_fd = bpf_map__fd(md->agentmetadata_map);
	md->endpoints_map_fd = bpf_map__fd(md->endpoints_map);

	if (bpf_map__unpin(md->xdpcap_hook_map, md->pcapfile) == 0) {
		TRN_LOG_INFO("unpin exiting pcap map file: %s", md->pcapfile);
	}

	int rc = bpf_map__pin(md->xdpcap_hook_map, md->pcapfile);

	if (rc != 0) {
		TRN_LOG_ERROR("Failed to pin xdpcap map.");
		return 1;
	}

	return 0;
}

int trn_agent_metadata_init(struct agent_user_metadata_t *md, char *itf,
			    char *agent_kern_path, int xdp_flags)
{
	int rc;
	struct rlimit r = { RLIM_INFINITY, RLIM_INFINITY };
	struct bpf_prog_load_attr prog_load_attr = { .prog_type =
							     BPF_PROG_TYPE_XDP,
						     .file = agent_kern_path };
	__u32 info_len = sizeof(md->info);

	md->xdp_flags = xdp_flags;

	if (setrlimit(RLIMIT_MEMLOCK, &r)) {
		TRN_LOG_ERROR("setrlimit(RLIMIT_MEMLOCK)");
		return 1;
	}

	snprintf(md->pcapfile, sizeof(md->pcapfile),
		 "/sys/fs/bpf/%s_transit_agent_pcap", itf);

	md->ifindex = if_nametoindex(itf);
	if (!md->ifindex) {
		TRN_LOG_ERROR("Error retrieving index of interface");
		return 1;
	}

	if (bpf_prog_load_xattr(&prog_load_attr, &md->obj, &md->prog_fd)) {
		TRN_LOG_ERROR("Error loading bpf: %s", agent_kern_path);
		return 1;
	}

	rc = trn_agent_bpf_maps_init(md);

	if (rc != 0) {
		return 1;
	}

	if (!md->prog_fd) {
		TRN_LOG_ERROR("load_bpf_file: %s", strerror(errno));
		return 1;
	}

	if (bpf_set_link_xdp_fd(md->ifindex, md->prog_fd, xdp_flags) < 0) {
		TRN_LOG_ERROR("link set xdp fd failed");
		return 1;
	}

	rc = bpf_obj_get_info_by_fd(md->prog_fd, &md->info, &info_len);
	if (rc != 0) {
		TRN_LOG_ERROR("can't get prog info - %s.", strerror(errno));
		return 1;
	}
	md->prog_id = md->info.id;

	return 0;
}

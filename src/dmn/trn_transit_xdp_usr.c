// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_agent_xdp_usr.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief User space APIs to program transit xdp program (switches and
 * routers)
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

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <linux/if.h>

#include "trn_transit_xdp_usr.h"
#include "trn_log.h"

int trn_user_metadata_free(struct user_metadata_t *md)
{
	__u32 curr_prog_id = 0;

	if (bpf_map__unpin(md->xdpcap_hook_map, md->pcapfile)) {
		TRN_LOG_ERROR("Failed to unpin the pcap map file %s.",
			      md->pcapfile);
		return 1;
	}

	if (bpf_get_link_xdp_id(md->ifindex, &curr_prog_id, md->xdp_flags)) {
		TRN_LOG_ERROR("bpf_get_link_xdp_id failed");
		return 1;
	}
	if (md->prog_id == curr_prog_id)
		bpf_set_link_xdp_fd(md->ifindex, -1, md->xdp_flags);
	else if (!curr_prog_id)
		TRN_LOG_WARN("couldn't find a prog id on a given interface\n");
	else
		TRN_LOG_WARN("program on interface changed, not removing\n");
	return 0;
}

int trn_bpf_maps_init(struct user_metadata_t *md)
{
	md->networks_map = bpf_map__next(NULL, md->obj);
	md->vpc_map = bpf_map__next(md->networks_map, md->obj);
	md->endpoints_map = bpf_map__next(md->vpc_map, md->obj);
	md->hosted_endpoints_iface_map =
		bpf_map__next(md->endpoints_map, md->obj);
	md->interface_config_map =
		bpf_map__next(md->hosted_endpoints_iface_map, md->obj);
	md->xdpcap_hook_map = bpf_map__next(md->interface_config_map, md->obj);

	if (!md->networks_map || !md->vpc_map || !md->endpoints_map ||
	    !md->hosted_endpoints_iface_map || !md->interface_config_map ||
	    !md->xdpcap_hook_map) {
		TRN_LOG_ERROR("Failure finding maps objects.");
		return 1;
	}

	md->networks_map_fd = bpf_map__fd(md->networks_map);
	md->vpc_map_fd = bpf_map__fd(md->vpc_map);
	md->endpoints_map_fd = bpf_map__fd(md->endpoints_map);
	md->interface_config_map_fd = bpf_map__fd(md->interface_config_map);
	md->hosted_endpoints_iface_map_fd =
		bpf_map__fd(md->hosted_endpoints_iface_map);

	if (bpf_map__unpin(md->xdpcap_hook_map, md->pcapfile) == 0) {
		TRN_LOG_INFO("unpin exiting pcap map file: %s", md->pcapfile);
	}

	int rc = bpf_map__pin(md->xdpcap_hook_map, md->pcapfile);

	if (rc != 0) {
		TRN_LOG_ERROR("Failed to pin xdpcap map to %s", md->pcapfile);
		return 1;
	}

	return 0;
}

int trn_update_network(struct user_metadata_t *md, struct network_key_t *netkey,
		       struct network_t *net)
{
	netkey->prefixlen += 64; /* tunid size */
	int err = bpf_map_update_elem(md->networks_map_fd, netkey, net, 0);
	if (err) {
		TRN_LOG_ERROR("Store network mapping failed (err:%d)", err);
		return 1;
	}
	return 0;
}

int trn_update_endpoint(struct user_metadata_t *md,
			struct endpoint_key_t *epkey, struct endpoint_t *ep)
{
	int err = bpf_map_update_elem(md->endpoints_map_fd, epkey, ep, 0);
	if (err) {
		TRN_LOG_ERROR("Store endpoint mapping failed (err:%d).", err);
		return 1;
	}
	return 0;
}

int trn_update_vpc(struct user_metadata_t *md, struct vpc_key_t *vpckey,
		   struct vpc_t *vpc)
{
	int err = bpf_map_update_elem(md->vpc_map_fd, vpckey, vpc, 0);
	if (err) {
		TRN_LOG_ERROR("Store VPCs mapping failed (err:%d).", err);
		return 1;
	}
	return 0;
}

int trn_get_network(struct user_metadata_t *md, struct network_key_t *netkey,
		    struct network_t *net)
{
	netkey->prefixlen += 64; /* tunid size */
	int err = bpf_map_lookup_elem(md->networks_map_fd, netkey, net);
	if (err) {
		TRN_LOG_ERROR("Querying network mapping failed (err:%d).", err);
		return 1;
	}
	return 0;
}

int trn_get_endpoint(struct user_metadata_t *md, struct endpoint_key_t *epkey,
		     struct endpoint_t *ep)
{
	int err = bpf_map_lookup_elem(md->endpoints_map_fd, epkey, ep);
	if (err) {
		TRN_LOG_ERROR("Querying endpoint mapping failed (err:%d).",
			      err);
		return 1;
	}
	return 0;
}

int trn_get_vpc(struct user_metadata_t *md, struct vpc_key_t *vpckey,
		struct vpc_t *vpc)
{
	int err = bpf_map_lookup_elem(md->vpc_map_fd, vpckey, vpc);
	if (err) {
		TRN_LOG_ERROR("Querying vpc mapping failed (err:%d).", err);
		return 1;
	}
	return 0;
}

int trn_user_metadata_init(struct user_metadata_t *md, char *itf,
			   char *kern_path, int xdp_flags)
{
	int rc;
	struct rlimit r = { RLIM_INFINITY, RLIM_INFINITY };
	struct bpf_prog_load_attr prog_load_attr = { .prog_type =
							     BPF_PROG_TYPE_XDP,
						     .file = kern_path };
	__u32 info_len = sizeof(md->info);
	md->xdp_flags = xdp_flags;

	if (setrlimit(RLIMIT_MEMLOCK, &r)) {
		TRN_LOG_ERROR("setrlimit(RLIMIT_MEMLOCK)");
		return 1;
	}

	snprintf(md->pcapfile, sizeof(md->pcapfile),
		 "/sys/fs/bpf/%s_transit_pcap", itf);

	md->ifindex = if_nametoindex(itf);
	if (!md->ifindex) {
		TRN_LOG_ERROR("if_nametoindex");
		return 1;
	}

	md->eth.ip = trn_get_interface_ipv4(md->ifindex);
	md->eth.iface_index = md->ifindex;

	if (bpf_prog_load_xattr(&prog_load_attr, &md->obj, &md->prog_fd)) {
		TRN_LOG_ERROR("Error loading bpf: %s", kern_path);
		return 1;
	}

	rc = trn_bpf_maps_init(md);

	if (rc != 0) {
		return 1;
	}

	if (!md->prog_fd) {
		TRN_LOG_ERROR("load_bpf_file: %s.", strerror(errno));
		return 1;
	}

	if (bpf_set_link_xdp_fd(md->ifindex, md->prog_fd, md->xdp_flags) < 0) {
		TRN_LOG_ERROR("link set xdp fd failed - %s.", strerror(errno));
		return 1;
	}

	rc = bpf_obj_get_info_by_fd(md->prog_fd, &md->info, &info_len);
	if (rc != 0) {
		TRN_LOG_ERROR("can't get prog info - %s.", strerror(errno));
		return rc;
	}
	md->prog_id = md->info.id;
	int k = 0;

	rc = bpf_map_update_elem(md->interface_config_map_fd, &k, &md->eth, 0);
	if (rc != 0) {
		TRN_LOG_ERROR("Failed to store interface index.");
		return 1;
	}

	return 0;
}

uint32_t trn_get_interface_ipv4(int itf_idx)
{
	int fd;
	struct ifreq ifr;

	fd = socket(AF_INET, SOCK_DGRAM, 0);

	/* IPv4 IP address */
	ifr.ifr_addr.sa_family = AF_INET;

	if_indextoname(itf_idx, ifr.ifr_name);
	ioctl(fd, SIOCGIFADDR, &ifr);

	close(fd);

	return ((struct sockaddr_in *)&ifr.ifr_addr)->sin_addr.s_addr;
}
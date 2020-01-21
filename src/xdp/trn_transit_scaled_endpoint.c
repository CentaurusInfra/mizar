// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_transit_xdp.c
 * @author Sherif Abdelwahab (@zasherif)
 *
 * @brief Implements the Transit XDP program (switching and routing logic)
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

#include <linux/bpf.h>
#include <linux/if_arp.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <linux/if_vlan.h>
#include <linux/in.h>
#include <linux/ip.h>
#include <linux/ipv6.h>
#include <linux/pkt_cls.h>
#include <linux/socket.h>
#include <linux/tcp.h>
#include <linux/types.h>
#include <linux/udp.h>
#include <stddef.h>
#include <string.h>

#include "extern/bpf_endian.h"
#include "extern/bpf_helpers.h"

#include "trn_datamodel.h"
#include "trn_kern.h"
#include "trn_transit_xdp_stages_maps.h"

int _version SEC("version") = 1;

static __inline int trn_scaled_ep_decide(struct transit_packet *pkt)
{
	void *endpoints_map;
	struct endpoint_t *ep;
	struct endpoint_key_t epkey;
	__u32 d_addr;
	int map_idx = 0;
	__u32 remote_idx;
	__be64 tunnel_id = trn_vni_to_tunnel_id(pkt->geneve->vni);

	endpoints_map = bpf_map_lookup_elem(&endpoints_map_ref, &map_idx);
	if (!endpoints_map) {
		bpf_debug("[Scaled_EP:%d:] failed to find endpoints_map\n",
			  __LINE__);
		return XDP_ABORTED;
	}

	__builtin_memcpy(&epkey.tunip[0], &tunnel_id, sizeof(tunnel_id));
	epkey.tunip[2] = pkt->inner_ip->daddr;

	/* Get the scaled endpoint configuration */
	ep = bpf_map_lookup_elem(endpoints_map, &epkey);

	if (!ep) {
		bpf_debug(
			"[Scaled_EP:%d:] (BUG) failed to find scaled endpoint configuration\n",
			__LINE__);
		return XDP_ABORTED;
	}

	/* Simple hashing for now! */
	__u32 inhash = jhash_2words(pkt->inner_ip->saddr, pkt->inner_ip->daddr,
				    INIT_JHASH_SEED);

	if (ep->nremote_ips == 0) {
		bpf_debug(
			"[Scaled_EP] DROP: no backend attached to scaled endpoint 0x%x!\n",
			bpf_ntohl(pkt->inner_ip->daddr));
		return XDP_DROP;
	}

	remote_idx = inhash % ep->nremote_ips;

	if (remote_idx > TRAN_MAX_REMOTES - 1) {
		bpf_debug(
			"[Scaled_EP] DROP (BUG): Selected remote index [%d] "
			"is greater than maximum number of supported remote endpoints [%d]!\n",
			remote_idx, TRAN_MAX_REMOTES);
		return XDP_ABORTED;
	}

	d_addr = ep->remote_ips[remote_idx];

	bpf_debug("[Scaled_EP:%d:] scaled endpoint to 0x%x!!\n", __LINE__,
		  bpf_ntohl(d_addr));

	return XDP_DROP;
}

static __inline int trn_sep_process_inner_ip(struct transit_packet *pkt)
{
	pkt->inner_ip = (void *)pkt->inner_eth + pkt->inner_eth_off;

	if (pkt->inner_ip + 1 > pkt->data_end) {
		bpf_debug("[Scaled_EP:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	return trn_scaled_ep_decide(pkt);
}

static __inline int trn_sep_process_inner_eth(struct transit_packet *pkt)
{
	pkt->inner_eth = (void *)pkt->geneve + pkt->gnv_hdr_len;
	pkt->inner_eth_off = sizeof(*pkt->inner_eth);

	if (pkt->inner_eth + 1 > pkt->data_end) {
		bpf_debug("[Scaled_EP:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	if (pkt->eth->h_proto != bpf_htons(ETH_P_IP)) {
		bpf_debug(
			"[Scaled_EP:%d:0x%x] DROP: unsupported inner packet: [0x%x]\n",
			__LINE__, bpf_ntohl(pkt->itf_ipv4),
			bpf_ntohs(pkt->eth->h_proto));
		return XDP_DROP;
	}

	return trn_sep_process_inner_ip(pkt);
}

static __inline int trn_sep_process_geneve(struct transit_packet *pkt)
{
	pkt->geneve = (void *)pkt->udp + sizeof(*pkt->udp);
	if (pkt->geneve + 1 > pkt->data_end) {
		bpf_debug("[Scaled_EP:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	pkt->gnv_opt_len = pkt->geneve->opt_len * 4;
	pkt->gnv_hdr_len = sizeof(*pkt->geneve) + pkt->gnv_opt_len;
	pkt->rts_opt = (void *)&pkt->geneve->options[0];

	if (pkt->rts_opt + 1 > pkt->data_end) {
		bpf_debug("[Scaled_EP:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	// TODO: process options

	return trn_sep_process_inner_eth(pkt);
}

static __inline int trn_sep_process_udp(struct transit_packet *pkt)
{
	/* Get the UDP header */
	pkt->udp = (void *)pkt->ip + sizeof(*pkt->ip);

	if (pkt->udp + 1 > pkt->data_end) {
		bpf_debug("[Scaled_EP:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	return trn_sep_process_geneve(pkt);
}

static __inline int trn_sep_process_ip(struct transit_packet *pkt)
{
	/* Get the IP header */
	pkt->ip = (void *)pkt->eth + pkt->eth_off;

	if (pkt->ip + 1 > pkt->data_end) {
		bpf_debug("[Scaled_EP:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	return trn_sep_process_udp(pkt);
}

static __inline int trn_sep_process_eth(struct transit_packet *pkt)
{
	pkt->eth = pkt->data;
	pkt->eth_off = sizeof(*pkt->eth);

	if (pkt->data + pkt->eth_off > pkt->data_end) {
		bpf_debug("[Scaled_EP:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	return trn_sep_process_ip(pkt);
}

SEC("transit_scaled_endpoint")
int _transit_scaled_endpoint(struct xdp_md *ctx)
{
	/* Simple scaled endpoint implementation */

	void *interface_config_map;
	struct transit_packet pkt;
	int map_idx = 0;
	pkt.data = (void *)(long)ctx->data;
	pkt.data_end = (void *)(long)ctx->data_end;
	pkt.xdp = ctx;

	struct tunnel_iface_t *itf;

	interface_config_map =
		bpf_map_lookup_elem(&interface_config_map_ref, &map_idx);
	if (!interface_config_map) {
		bpf_debug(
			"[Scaled_EP:%d:] failed to find interface_config_map\n",
			__LINE__);
		return XDP_ABORTED;
	}

	int k = 0;
	itf = bpf_map_lookup_elem(interface_config_map, &k);

	if (!itf) {
		bpf_debug("[Scaled_EP:%d:] ABORTED: Bad configuration\n",
			  __LINE__);
		return XDP_ABORTED;
	}

	pkt.itf_ipv4 = itf->ip;
	pkt.itf_idx = itf->iface_index;

	return trn_sep_process_eth(&pkt);
}

char _license[] SEC("license") = "GPL";

// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_transit_xdp_hardware_offload.c
 * @author Peng Yang (@yangpenger)
 *
 * @brief Offloads functions of bouncers and dividers about Direct Path.
 *        This offloaded program works before original Transit XDP program, 
 * 		  i.e., multiple programs on the same XDP interface.
 * 		  Thus, non-offload functions are performed by original Transit XDP program.
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

int _version SEC("version") = 1;

struct bpf_map_def SEC("maps") networks_offload_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct network_key_t),
	.value_size = sizeof(struct network_offload_t),
	.max_entries = 1000001,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(networks_offload_map, struct network_key_t, struct network_offload_t);

struct bpf_map_def SEC("maps") vpc_offload_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct vpc_key_t),
	.value_size = sizeof(struct vpc_offload_t),
	.max_entries = 1000001,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(vpc_offload_map, struct vpc_key_t, struct vpc_offload_t);

struct bpf_map_def SEC("maps") endpoints_offload_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct endpoint_key_t),
	.value_size = sizeof(struct endpoint_offload_t),
	.max_entries = 1000001,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(endpoints_offload_map, struct endpoint_key_t, struct endpoint_offload_t);

struct bpf_map_def SEC("maps") interface_config_offload_map = {
	.type = BPF_MAP_TYPE_ARRAY,
	.key_size = sizeof(int),
	.value_size = sizeof(struct tunnel_iface_t),
	.max_entries = 1,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(interface_config_offload_map, int, struct tunnel_iface_t);

static __inline int trn_rewrite_remote_mac(struct transit_packet *pkt)
{
	/* The TTL must have been decremented before this step, Drop the
	packet if TTL is zero */
	if (!pkt->ip->ttl)
		return XDP_DROP;

	struct endpoint_offload_t *remote_ep;
	struct endpoint_key_t epkey;
	epkey.tunip[0] = 0;
	epkey.tunip[1] = 0;
	epkey.tunip[2] = pkt->ip->daddr;
	/* Get the remote_mac address based on the value of the outer dest IP */
	remote_ep = bpf_map_lookup_elem(&endpoints_offload_map, &epkey);
	if (!remote_ep) {
		return XDP_DROP;
	}

	trn_set_src_mac(pkt->data, pkt->eth->h_dest);
	trn_set_dst_mac(pkt->data, remote_ep->mac);

	if (pkt->ip->tos & IPTOS_MINCOST) {
		return XDP_PASS;
	}

	return XDP_TX;
}

static __inline int trn_router_handle_pkt(struct transit_packet *pkt,
					  __u32 inner_src_ip,
					  __u32 inner_dst_ip)
{
	__be64 tunnel_id = trn_vni_to_tunnel_id(pkt->geneve->vni);
	/* This is where we forward the packet to the transit router:  First lookup
	the network of the inner_ip->daddr, if found hash and forward to the
	transit switch of that network, OW forward to the transit router. */

	struct network_key_t nkey;
	struct network_offload_t *net;
	/* SmartNIC does not supporting BPF_MAP_TYPE_LPM_TRIE here, so match with a exact length (80). */
	nkey.prefixlen = 80;
	__builtin_memcpy(&nkey.nip[0], &tunnel_id, sizeof(tunnel_id));
	/* Obtain the network number by the mask. The subnet prefix length is 16. */
	nkey.nip[2] = inner_dst_ip & 0xFFFF;
	net = bpf_map_lookup_elem(&networks_offload_map, &nkey);

	if (net) {
		pkt->rts_opt->rts_data.host.ip = pkt->ip->daddr;
		__builtin_memcpy(pkt->rts_opt->rts_data.host.mac,
				 pkt->eth->h_dest, 6 * sizeof(unsigned char));

		if (net->nip[0] != nkey.nip[0] || net->nip[1] != nkey.nip[1]) {
			return XDP_DROP;
		}
		
		/* Only send to the first switch. */
		__u32 swidx = 0;
		trn_set_src_dst_ip_csum(pkt, pkt->ip->daddr,
					net->switches_ips[swidx]);

		return trn_rewrite_remote_mac(pkt);
	}

	/* Now forward the packet to the VPC router */
	struct vpc_key_t vpckey;
	struct vpc_offload_t *vpc;

	vpckey.tunnel_id = tunnel_id;
	vpc = bpf_map_lookup_elem(&vpc_offload_map, &vpckey);

	if (!vpc) {
		return XDP_DROP;
	}

	/* Only send to the first router. */
	__u32 routeridx = 0;
	trn_set_src_dst_ip_csum(pkt, pkt->ip->daddr,
				vpc->routers_ips[routeridx]);

	return trn_rewrite_remote_mac(pkt);
}


static __inline int trn_switch_handle_pkt(struct transit_packet *pkt,
					  __u32 inner_src_ip,
					  __u32 inner_dst_ip, __u32 orig_src_ip)
{
	__be64 tunnel_id = trn_vni_to_tunnel_id(pkt->geneve->vni);
	struct endpoint_offload_t *ep;
	struct endpoint_key_t epkey;

	__builtin_memcpy(&epkey.tunip[0], &tunnel_id, sizeof(tunnel_id));
	epkey.tunip[2] = inner_dst_ip;

	/* Get the remote_ip based on the value of the inner dest IP and VNI*/
	ep = bpf_map_lookup_elem(&endpoints_offload_map, &epkey);
	if (!ep) {
		if (pkt->scaled_ep_opt->type == TRN_GNV_SCALED_EP_OPT_TYPE &&
		    pkt->scaled_ep_opt->scaled_ep_data.msg_type ==
			    TRN_SCALED_EP_MODIFY)
			return XDP_PASS;
		
		return trn_router_handle_pkt(pkt, inner_src_ip, inner_dst_ip);
	}

	/* The packet may be sent first to a gw mac address */
	trn_set_dst_mac(pkt->inner_eth, ep->mac);

	// TODO: Currently all endpoints are attached to one host, for some
	// ep types, they will have multiple attachments (e.g. LB endpoint).
	if (ep->hosted_iface != -1) {
		return XDP_PASS;
	}

	if (ep->eptype == TRAN_SCALED_EP) {
		return XDP_PASS;
	}

	if (ep->nremote_ips == 0) {
		return XDP_DROP;
	}

	trn_set_src_dst_ip_csum(pkt, pkt->ip->daddr, ep->remote_ips[0]);

	return trn_rewrite_remote_mac(pkt);
}

static __inline int trn_process_inner_ip(struct transit_packet *pkt)
{
	pkt->inner_ip = (void *)pkt->inner_eth + pkt->inner_eth_off;
	__u32 ipproto;

	if (pkt->inner_ip + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	/* For whatever compiler reason, we need to perform reverse flow modification
	 in this function instead of trn_switch_handle_pkt so we keep the orig_src_ip */
	__u32 orig_src_ip = pkt->inner_ip->saddr;

	pkt->inner_ipv4_tuple.saddr = pkt->inner_ip->saddr;
	pkt->inner_ipv4_tuple.daddr = pkt->inner_ip->daddr;
	pkt->inner_ipv4_tuple.protocol = pkt->inner_ip->protocol;
	pkt->inner_ipv4_tuple.sport = 0;
	pkt->inner_ipv4_tuple.dport = 0;

	if (pkt->inner_ipv4_tuple.protocol == IPPROTO_TCP) {
		pkt->inner_tcp = (void *)pkt->inner_ip + sizeof(*pkt->inner_ip);
		if (pkt->inner_tcp + 1 > pkt->data_end) {
			return XDP_ABORTED;
		}

		pkt->inner_ipv4_tuple.sport = pkt->inner_tcp->source;
		pkt->inner_ipv4_tuple.dport = pkt->inner_tcp->dest;
	}

	if (pkt->inner_ipv4_tuple.protocol == IPPROTO_UDP) {
		pkt->inner_udp = (void *)pkt->inner_ip + sizeof(*pkt->inner_ip);
		if (pkt->inner_udp + 1 > pkt->data_end) {
			return XDP_ABORTED;
		}

		pkt->inner_ipv4_tuple.sport = pkt->inner_udp->source;
		pkt->inner_ipv4_tuple.dport = pkt->inner_udp->dest;
	}

	__be64 tunnel_id = trn_vni_to_tunnel_id(pkt->geneve->vni);

	/* Lookup the source endpoint*/
	struct endpoint_offload_t *src_ep;
	struct endpoint_key_t src_epkey;
	__builtin_memcpy(&src_epkey.tunip[0], &tunnel_id, sizeof(tunnel_id));
	src_epkey.tunip[2] = pkt->inner_ip->saddr;
	src_ep = bpf_map_lookup_elem(&endpoints_offload_map, &src_epkey);

	/* If this is not the source endpoint's host,
	skip reverse flow modification, or scaled endpoint modify handling */
	if (pkt->scaled_ep_opt->type == TRN_GNV_SCALED_EP_OPT_TYPE &&
	    pkt->scaled_ep_opt->scaled_ep_data.msg_type ==
		    TRN_SCALED_EP_MODIFY &&
	    src_ep && src_ep->hosted_iface != -1) {
		return XDP_PASS;
	}

	/* Check if we need to apply a reverse flow update */
	struct ipv4_tuple_t inner;
	__builtin_memcpy(&inner, &pkt->inner_ipv4_tuple,
			 sizeof(struct ipv4_tuple_t));

	return trn_switch_handle_pkt(pkt, pkt->inner_ip->saddr,
				     pkt->inner_ip->daddr, orig_src_ip);
}

static __inline int trn_process_inner_arp(struct transit_packet *pkt)
{
	unsigned char *sha;
	unsigned char *tha = NULL;
	struct endpoint_offload_t *ep;
	struct endpoint_key_t epkey;
	struct endpoint_offload_t *remote_ep;
	__u32 *sip, *tip;
	__u64 csum = 0;

	pkt->inner_arp = (void *)pkt->inner_eth + sizeof(*pkt->inner_eth);

	if (pkt->inner_arp + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	if (pkt->inner_arp->ar_pro != bpf_htons(ETH_P_IP) ||
	    pkt->inner_arp->ar_hrd != bpf_htons(ARPHRD_ETHER)) {
		return XDP_DROP;
	}

	if (pkt->inner_arp->ar_op != bpf_htons(ARPOP_REPLY) &&
	    pkt->inner_arp->ar_op != bpf_htons(ARPOP_REQUEST)) {
		return XDP_DROP;
	}

	if ((unsigned char *)(pkt->inner_arp + 1) > pkt->data_end) {
		return XDP_ABORTED;
	}

	sha = (unsigned char *)(pkt->inner_arp + 1);
	if (sha + ETH_ALEN > pkt->data_end) {
		return XDP_ABORTED;
	}

	sip = (__u32 *)(sha + ETH_ALEN);
	if (sip + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	tha = (unsigned char *)sip + sizeof(__u32);
	if (tha + ETH_ALEN > pkt->data_end) {
		return XDP_ABORTED;
	}

	tip = (__u32 *)(tha + ETH_ALEN);
	if ((void *)tip + sizeof(__u32) > pkt->data_end) {
		return XDP_ABORTED;
	}

	__be64 tunnel_id = trn_vni_to_tunnel_id(pkt->geneve->vni);

	__builtin_memcpy(&epkey.tunip[0], &tunnel_id, sizeof(tunnel_id));
	epkey.tunip[2] = *tip;
	ep = bpf_map_lookup_elem(&endpoints_offload_map, &epkey);
	/* Don't respond to arp if endpoint is not found, or it is local to host */
	if (!ep || ep->hosted_iface != -1 ||
	    pkt->inner_arp->ar_op != bpf_htons(ARPOP_REQUEST)) {
		return trn_switch_handle_pkt(pkt, *sip, *tip, *sip);
	}

	/* Respond to ARP */
	pkt->inner_arp->ar_op = bpf_htons(ARPOP_REPLY);
	trn_set_arp_ha(tha, sha);
	trn_set_arp_ha(sha, ep->mac);

	__u32 tmp_ip = *sip;
	*sip = *tip;
	*tip = tmp_ip;

	/* Set the sender mac address to the ep mac address */
	trn_set_src_mac(pkt->inner_eth, ep->mac);

	if (ep->eptype == TRAN_SIMPLE_EP) {
		/*Get the remote_ep address based on the value of the outer dest IP */
		epkey.tunip[0] = 0;
		epkey.tunip[1] = 0;
		epkey.tunip[2] = ep->remote_ips[0];
		remote_ep = bpf_map_lookup_elem(&endpoints_offload_map, &epkey);
		if (!remote_ep) {
			return XDP_DROP;
		}

		/* For a simple endpoint, Write the RTS option on behalf of the target endpoint */
		pkt->rts_opt->rts_data.host.ip = ep->remote_ips[0];
		__builtin_memcpy(pkt->rts_opt->rts_data.host.mac,
				 remote_ep->mac, 6 * sizeof(unsigned char));
	} else {
		trn_reset_rts_opt(pkt);
	}

	/* We need to lookup the endpoint again, since tip has changed */
	epkey.tunip[2] = *tip;
	ep = bpf_map_lookup_elem(&endpoints_offload_map, &epkey);

	return trn_switch_handle_pkt(pkt, *sip, *tip, *sip);
}

static __inline int trn_process_inner_eth(struct transit_packet *pkt)
{
	pkt->inner_eth = (void *)pkt->geneve + pkt->gnv_hdr_len;
	pkt->inner_eth_off = sizeof(*pkt->inner_eth);
	if (pkt->inner_eth + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	/* ARP */
	if (pkt->inner_eth->h_proto == bpf_htons(ETH_P_ARP)) {
		return trn_process_inner_arp(pkt);
	}

	if (pkt->eth->h_proto != bpf_htons(ETH_P_IP)) {
		return XDP_DROP;
	}

	return trn_process_inner_ip(pkt);
}

static __inline int trn_process_geneve(struct transit_packet *pkt)
{
	pkt->geneve = (void *)pkt->udp + sizeof(*pkt->udp);
	if (pkt->geneve + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	if (pkt->geneve->proto_type != bpf_htons(ETH_P_TEB)) {
		return XDP_PASS;
	}

	pkt->gnv_opt_len = pkt->geneve->opt_len * 4;
	pkt->gnv_hdr_len = sizeof(*pkt->geneve) + pkt->gnv_opt_len;
	pkt->rts_opt = (void *)&pkt->geneve->options[0];
	if (pkt->rts_opt + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	if (pkt->rts_opt->opt_class != TRN_GNV_OPT_CLASS) {
		return XDP_ABORTED;
	}

	// TODO: process options
	pkt->scaled_ep_opt = (void *)pkt->rts_opt + sizeof(*pkt->rts_opt);
	if (pkt->scaled_ep_opt + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	if (pkt->scaled_ep_opt->opt_class != TRN_GNV_OPT_CLASS) {
		return XDP_ABORTED;
	}

	return trn_process_inner_eth(pkt);
}

static __inline int trn_process_udp(struct transit_packet *pkt)
{
	/* Get the UDP header */
	pkt->udp = (void *)pkt->ip + sizeof(*pkt->ip);
	if (pkt->udp + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	if (pkt->udp->dest != GEN_DSTPORT) {
		return XDP_PASS;
	}

	return trn_process_geneve(pkt);
}

static __inline int trn_process_ip(struct transit_packet *pkt)
{
	/* Get the IP header */
	pkt->ip = (void *)pkt->eth + pkt->eth_off;
	if (pkt->ip + 1 > pkt->data_end) {
		return XDP_ABORTED;
	}

	if (pkt->ip->protocol != IPPROTO_UDP) {
		return XDP_PASS;
	}

	if (!pkt->ip->ttl) {
		return XDP_DROP;
	}

	/* Only process packets designated to this interface!
	 * In functional tests - relying on docker0 - we see such packets!
	 */
	if (pkt->ip->daddr != pkt->itf_ipv4) {
		return XDP_DROP;
	}

	return trn_process_udp(pkt);
}

static __inline int trn_process_eth(struct transit_packet *pkt)
{
	pkt->eth = pkt->data;
	pkt->eth_off = sizeof(*pkt->eth);
	if (pkt->data + pkt->eth_off > pkt->data_end) {
		return XDP_ABORTED;
	}

	if (pkt->eth->h_proto != bpf_htons(ETH_P_IP)) {
		return XDP_PASS;
	}

	return trn_process_ip(pkt);
}

SEC("transit")
int _transit(struct xdp_md *ctx)
{
	struct transit_packet pkt;
	pkt.data = (void *)(long)ctx->data;
	pkt.data_end = (void *)(long)ctx->data_end;
	pkt.xdp = ctx;

	struct tunnel_iface_t *itf;

	int k = 0;
	itf = bpf_map_lookup_elem(&interface_config_offload_map, &k);
	if (!itf) {
		return XDP_ABORTED;
	}

	pkt.itf_ipv4 = itf->ip;
	pkt.itf_idx = itf->iface_index;

	return trn_process_eth(&pkt);
}

char _license[] SEC("license") = "GPL";

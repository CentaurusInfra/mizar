// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_agent_xdp.c
 * @author Sherif Abdelwahab (@zasherif)
 *
 * @brief Transit agent XDP program
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
#include "trn_agent_xdp_maps.h"
#include "trn_kern.h"

int _version SEC("version") = 1;
#define SPORT_MAX 6553
#define SPORT_MIN 1024
#define SPORT_BASE (SPORT_MAX - SPORT_MIN)

static __inline int trn_encapsulate(struct transit_packet *pkt,
				    struct agent_metadata_t *metadata,
				    __be64 tun_id, __u32 in_src_ip,
				    __u32 in_dst_ip)
{
	struct endpoint_t *r_ep;
	struct endpoint_key_t r_epkey;
	__u16 s_port;
	__u32 d_addr;
	__u64 c_sum = 0;
	int old_size = pkt->data_end - pkt->data;

	/* Compute the source port and the transit switch address based on a hash
   * of the inner ip */
	__u32 inhash = jhash_2words(in_src_ip, in_dst_ip, INIT_JHASH_SEED);
	s_port = SPORT_MIN + (inhash % SPORT_BASE);

	if (s_port < SPORT_MIN || s_port > SPORT_MAX) {
		return XDP_DROP;
	}

	if (metadata->net.nswitches == 0) {
		bpf_debug(
			"[Agent:%ld.0x%x] DROP (BUG): No transit switch to send packet to!\n",
			pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4));
		return XDP_DROP;
	}

	__u32 sw_idx = inhash % metadata->net.nswitches;

	if (sw_idx > TRAN_MAX_NSWITCH - 1) {
		bpf_debug("[Agent:] DROP (BUG): Selected switch index [%d] "
			  "is greater than maximum number of switches [%d]!\n",
			  sw_idx, TRAN_MAX_NSWITCH);
		return XDP_DROP;
	}

	d_addr = metadata->net.switches_ips[sw_idx];

	/* Get the endpoint of the transit switch for outer dst mac */
	r_epkey.tunip[0] = 0;
	r_epkey.tunip[1] = 0;
	r_epkey.tunip[2] = d_addr;
	r_ep = bpf_map_lookup_elem(&endpoints_map, &r_epkey);

	if (!r_ep) {
		bpf_debug("[Agent:%ld.0x%x] DROP (BUG): Missing mac "
			  " information for transit switches!\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4));
		return XDP_DROP;
	}

	/* Readjust the packet size to fit the outer headers */
	int outer_hdr_size = sizeof(*pkt->geneve) + sizeof(*pkt->udp) +
			     sizeof(*pkt->ip) + sizeof(*pkt->eth);
	int outer_ip_payload = sizeof(*pkt->geneve) + sizeof(*pkt->udp) +
			       sizeof(*pkt->ip) + old_size;
	int outer_udp_payload =
		sizeof(*pkt->geneve) + sizeof(*pkt->udp) + old_size;

	if (bpf_xdp_adjust_head(pkt->xdp, 0 - outer_hdr_size)) {
		bpf_debug(
			"[Agent:%ld.0x%x] DROP (BUG): Failure adjusting packet header!\n",
			pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4));
		return XDP_DROP;
	}

	pkt->data = (void *)(long)pkt->xdp->data;
	pkt->data_end = (void *)(long)pkt->xdp->data_end;

	pkt->eth = pkt->data;
	pkt->eth_off = sizeof(*pkt->eth);

	pkt->ip = (void *)pkt->eth + sizeof(*pkt->eth);
	pkt->udp = (void *)pkt->ip + sizeof(*pkt->ip);
	pkt->geneve = (void *)pkt->udp + sizeof(*pkt->udp);

	if (pkt->eth + 1 > pkt->data_end || pkt->ip + 1 > pkt->data_end ||
	    pkt->udp + 1 > pkt->data_end || pkt->geneve + 1 > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	/* Populate the outer header fields */
	pkt->eth->h_proto = bpf_htons(ETH_P_IP);

	trn_set_dst_mac(pkt->data, r_ep->mac);
	trn_set_src_mac(pkt->data, metadata->eth.mac);

	pkt->ip->version = 4;
	pkt->ip->ihl = sizeof(*pkt->ip) >> 2;
	pkt->ip->frag_off = 0;
	pkt->ip->protocol = IPPROTO_UDP;
	pkt->ip->check = 0;
	pkt->ip->tos = 0;
	pkt->ip->tot_len = bpf_htons(outer_ip_payload);
	pkt->ip->daddr = d_addr;
	pkt->ip->saddr = metadata->eth.ip;
	pkt->ip->ttl = pkt->inner_ttl;

	c_sum = 0;
	trn_ipv4_csum_inline(pkt->ip, &c_sum);
	pkt->ip->check = c_sum;

	pkt->udp->source = bpf_htons(
		s_port); // TODO: a hash value based on inner IP packet
	pkt->udp->dest = GEN_DSTPORT;
	pkt->udp->len = bpf_htons(outer_udp_payload);

	pkt->geneve->opt_len = 0;
	pkt->geneve->ver = 0;
	pkt->geneve->rsvd1 = 0;
	pkt->geneve->rsvd2 = 0;
	pkt->geneve->oam = 0;
	pkt->geneve->critical = 0;
	pkt->geneve->proto_type = bpf_htons(ETH_P_TEB);
	trn_tunnel_id_to_vni(tun_id, pkt->geneve->vni);

	/* If the source and dest address of the tunneled packet is the
	 * same, then this host is also a transit switch. Just invoke the
	 * transit XDP program by a tail call;
	 */

	if (pkt->ip->saddr == pkt->ip->daddr) {
		bpf_debug(
			"[Agent:%ld.0x%x] TAILCALL: transit switch on same host. Tunnel to dst=[%d].\n",
			pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			bpf_htonl(pkt->ip->daddr));

		__u32 key = XDP_TRANSIT;
		bpf_tail_call(pkt->xdp, &jmp_table, key);
	}

	/* Send the packet on the egress of the tunneling interface */
	bpf_debug("[Agent:%ld.0x%x] REDIRECT: Tunnel to dst=[%d].\n",
		  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
		  bpf_htonl(pkt->ip->daddr));
	return bpf_redirect(metadata->eth.iface_index, 0);
}

static __inline int trn_redirect(struct transit_packet *pkt, __u32 inner_src_ip,
				 __u32 inner_dst_ip)
{
	struct agent_metadata_t *md = pkt->agent_md;
	__be64 tunnel_id = pkt->agent_ep_tunid;

	return trn_encapsulate(pkt, md, tunnel_id, inner_src_ip, inner_dst_ip);
}

static __inline int trn_process_inner_ip(struct transit_packet *pkt)
{
	pkt->inner_ip = (void *)pkt->inner_eth + pkt->inner_eth_off;
	__u32 ipproto;

	if (pkt->inner_ip + 1 > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	ipproto = pkt->inner_ip->protocol;
	pkt->inner_ttl = pkt->inner_ip->ttl;
	// TODO: switch parse inner UDP/TCP

	return trn_redirect(pkt, pkt->inner_ip->saddr, pkt->inner_ip->daddr);
}

static __inline int trn_process_arp(struct transit_packet *pkt)
{
	unsigned char *sha;
	unsigned char *tha = NULL;
	__u32 *sip;
	__u32 *tip;

	pkt->inner_arp = (void *)pkt->inner_eth + sizeof(*pkt->inner_eth);

	if (pkt->inner_arp + 1 > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	if (pkt->inner_arp->ar_pro != bpf_htons(ETH_P_IP) ||
	    pkt->inner_arp->ar_hrd != bpf_htons(ARPHRD_ETHER)) {
		bpf_debug(
			"[Agent:%ld.0x%x] DROP: unsupported ARP protocol or hardware!\n",
			pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4));
		return XDP_DROP;
	}

	if (pkt->inner_arp->ar_op != bpf_htons(ARPOP_REPLY) &&
	    pkt->inner_arp->ar_op != bpf_htons(ARPOP_REQUEST)) {
		bpf_debug(
			"[Agent:%ld.0x%x] DROP: unsupported ARP OP code [0x%x]\n",
			pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			pkt->inner_arp->ar_op);
		return XDP_DROP;
	}

	if ((unsigned char *)(pkt->inner_arp + 1) > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	sha = (unsigned char *)(pkt->inner_arp + 1);

	if (sha + ETH_ALEN > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	sip = (__u32 *)(sha + ETH_ALEN);

	if (sip + 1 > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	tha = (unsigned char *)sip + sizeof(__u32);

	if (tha + ETH_ALEN > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	tip = (__u32 *)(tha + ETH_ALEN);

	if ((void *)tip + sizeof(__u32) > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	return trn_redirect(pkt, *sip, *tip);
}

static __inline int trn_process_inner_eth(struct transit_packet *pkt)
{
	pkt->inner_eth = (void *)pkt->data;
	pkt->inner_eth_off = sizeof(*pkt->inner_eth);

	if (pkt->inner_eth + 1 > pkt->data_end) {
		bpf_debug("[Agent:%ld.0x%x] ABORTED: Bad offset [%d]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  __LINE__);
		return XDP_ABORTED;
	}

	/* ARP */
	if (pkt->inner_eth->h_proto == bpf_htons(ETH_P_ARP)) {
		bpf_debug("[Agent:%ld.0x%x] Processing ARP\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4));
		return ({ trn_process_arp(pkt); });
	}

	if (pkt->inner_eth->h_proto != bpf_htons(ETH_P_IP)) {
		bpf_debug("[Agent:%ld.0x%x] DROP: unsupported"
			  " inner packet type [0x%x]\n",
			  pkt->agent_ep_tunid, bpf_ntohl(pkt->agent_ep_ipv4),
			  bpf_ntohs(pkt->inner_eth->h_proto));
		return XDP_DROP;
	}

	bpf_debug("[Agent:%ld.0x%x] Processing IP\n", pkt->agent_ep_tunid,
		  bpf_ntohl(pkt->agent_ep_ipv4));

	return trn_process_inner_ip(pkt);
}

SEC("agent")
int _agent(struct xdp_md *ctx)
{
	struct transit_packet pkt;
	pkt.data = (void *)(long)ctx->data;
	pkt.data_end = (void *)(long)ctx->data_end;
	pkt.xdp = ctx;
	pkt.agent_ep_ipv4 = -1;
	pkt.agent_ep_tunid = -1;
	pkt.inner_ttl = TRN_DEFAULT_TTL; // Default in case of non inner IP
	/* Get the metadata of the agent */
	int key = 0;
	pkt.agent_md = bpf_map_lookup_elem(&agentmetadata_map, &key);
	if (!pkt.agent_md) {
		bpf_debug("DROP (BUG): Agent metadata is missing\n");
		return XDP_DROP;
	}

	__builtin_memcpy(&pkt.agent_ep_tunid, &pkt.agent_md->epkey.tunip[0],
			 sizeof(__be64));
	pkt.agent_ep_ipv4 = pkt.agent_md->epkey.tunip[2];
	bpf_debug("[Agent:%ld.0x%x]\n", pkt.agent_ep_tunid,
		  bpf_ntohl(pkt.agent_ep_ipv4));

	int action = trn_process_inner_eth(&pkt);

	if (action == XDP_PASS)
		return xdpcap_exit(ctx, &xdpcap_hook, XDP_PASS);

	if (action == XDP_DROP)
		return xdpcap_exit(ctx, &xdpcap_hook, XDP_DROP);

	if (action == XDP_TX)
		return xdpcap_exit(ctx, &xdpcap_hook, XDP_TX);

	if (action == XDP_ABORTED)
		return xdpcap_exit(ctx, &xdpcap_hook, XDP_ABORTED);

	if (action == XDP_REDIRECT)
		return xdpcap_exit(ctx, &xdpcap_hook, XDP_REDIRECT);

	return xdpcap_exit(ctx, &xdpcap_hook, XDP_PASS);
}

char _license[] SEC("license") = "GPL";

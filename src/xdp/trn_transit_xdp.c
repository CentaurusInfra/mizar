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
#include "trn_transit_xdp_maps.h"
#include "trn_kern.h"

int _version SEC("version") = 1;

static __inline int trn_rewrite_remote_mac(struct transit_packet *pkt)
{
	/* The TTL must have been decremented before this step, Drop the
	packet if TTL is zero */
	if (!pkt->ip->ttl)
		return XDP_DROP;

	struct endpoint_t *remote_ep;
	struct endpoint_key_t epkey;
	epkey.tunip[0] = 0;
	epkey.tunip[1] = 0;
	epkey.tunip[2] = pkt->ip->daddr;
	/* Get the remote_mac address based on the value of the outer dest IP */
	remote_ep = bpf_map_lookup_elem(&endpoints_map, &epkey);

	if (!remote_ep) {
		bpf_debug("[Transit:%d:] DROP: "
			  "Failed to find remote MAC address\n",
			  __LINE__);
		return XDP_DROP;
	}

	trn_set_src_mac(pkt->data, pkt->eth->h_dest);
	trn_set_dst_mac(pkt->data, remote_ep->mac);
	return XDP_TX;
}

static __inline int trn_decapsulate_and_redirect(struct transit_packet *pkt,
						 int ifindex)
{
	int outer_header_size = sizeof(*pkt->geneve) + sizeof(*pkt->udp) +
				sizeof(*pkt->ip) + sizeof(*pkt->eth);

	if (bpf_xdp_adjust_head(pkt->xdp, 0 + outer_header_size)) {
		bpf_debug(
			"[Transit:%d:0x%x] DROP: failed to adjust packet head.\n",
			__LINE__, bpf_ntohl(pkt->itf_ipv4));
		return XDP_DROP;
	}
	bpf_debug("[Transit:%d:0x%x] REDIRECT: itf=[%d].\n", __LINE__,
		  bpf_ntohl(pkt->itf_ipv4), ifindex);
	return bpf_redirect(ifindex, 0);
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
	struct network_t *net;
	nkey.prefixlen = 96;
	__builtin_memcpy(&nkey.nip[0], &tunnel_id, sizeof(tunnel_id));
	nkey.nip[2] = inner_dst_ip;
	net = bpf_map_lookup_elem(&networks_map, &nkey);

	bpf_debug("[Transit::] LPM lookup key [0x%x:0x%x]!\n", nkey.prefixlen,
		  nkey.nip[2]);

	if (net) {
		bpf_debug("[Transit::] LPM found [0x%x:0x%x:0x%x]!\n",
			  net->nip[0], net->nip[1], net->nip[2]);

		if (net->nip[0] != nkey.nip[0] || net->nip[1] != nkey.nip[1]) {
			bpf_debug(
				"[Transit:%d:] DROP (BUG): Network tunnel_id cannot be different from key!\n",
				__LINE__);
			return XDP_DROP;
		}

		__u32 swidx = jhash_2words(inner_src_ip, inner_dst_ip,
					   INIT_JHASH_SEED) %
			      net->nswitches;

		if (swidx > TRAN_MAX_NSWITCH - 1) {
			bpf_debug(
				"[Transit:%d:] DROP (BUG): hash switch index is greater than maximum number of switches!\n",
				__LINE__);
			return XDP_DROP;
		}

		bpf_debug("[Transit:%d:] Sending packet to switch!\n",
			  __LINE__);

		trn_set_src_dst_ip_csum(pkt, pkt->ip->daddr,
					net->switches_ips[swidx]);
		return trn_rewrite_remote_mac(pkt);
	}

	/* Now forward the packet to the VPC router */
	struct vpc_key_t vpckey;
	struct vpc_t *vpc;

	vpckey.tunnel_id = tunnel_id;
	vpc = bpf_map_lookup_elem(&vpc_map, &vpckey);

	if (!vpc) {
		bpf_debug(
			"[Transit:%d:] DROP (BUG): Missing VPC router data!\n",
			__LINE__);
		return XDP_DROP;
	}

	__u32 routeridx =
		jhash_2words(inner_src_ip, inner_dst_ip, INIT_JHASH_SEED) %
		vpc->nrouters;

	if (routeridx > TRAN_MAX_NROUTER - 1) {
		bpf_debug(
			"[Transit:%d:] DROP (BUG): hash router index is greater than maximum number of routers!",
			__LINE__);
		return XDP_DROP;
	}

	bpf_debug("[Transit:%d:] Sending packet to router!\n", __LINE__);
	trn_set_src_dst_ip_csum(pkt, pkt->ip->daddr,
				vpc->routers_ips[routeridx]);
	return trn_rewrite_remote_mac(pkt);
}

static __inline int trn_switch_handle_pkt(struct transit_packet *pkt,
					  __u32 inner_src_ip,
					  __u32 inner_dst_ip)
{
	/* dump debug received packet header info */
	bpf_debug("[Transit::0x%x] RX: {src=0x%x, dst=0x%x}/\n",
		  bpf_ntohl(pkt->itf_ipv4), bpf_ntohl(pkt->ip->saddr),
		  bpf_ntohl(pkt->ip->daddr));
	bpf_debug("[Transit::0x%x] RX: {vni:0x%x}/\n", bpf_ntohl(pkt->itf_ipv4),
		  trn_vni_to_tunnel_id(pkt->geneve->vni));
	bpf_debug("[Transit::0x%x] RX: {in.src=0x%x, in.dst=0x%x}\n",
		  bpf_ntohl(pkt->itf_ipv4), bpf_ntohl(inner_src_ip),
		  bpf_ntohl(inner_dst_ip));

	__be64 tunnel_id = trn_vni_to_tunnel_id(pkt->geneve->vni);
	struct endpoint_t *ep;
	struct endpoint_key_t epkey;

	__builtin_memcpy(&epkey.tunip[0], &tunnel_id, sizeof(tunnel_id));
	epkey.tunip[2] = inner_dst_ip;

	/* Get the remote_ip based on the value of the inner dest IP and VNI*/
	ep = bpf_map_lookup_elem(&endpoints_map, &epkey);

	if (!ep) {
		return trn_router_handle_pkt(pkt, inner_src_ip, inner_dst_ip);
	}

	/* The packet may be sent first to a gw mac address */
	trn_set_dst_mac(pkt->inner_eth, ep->mac);

	// TODO: Currently all endpoints are attached to one host, for some
	// ep types, they will have multiple attachments (e.g. LB endpoint).
	if (ep->hosted_iface != -1) {
		bpf_debug(
			"[Transit::0x%x] This is the ep host dst=[%d] @ itf=[%d]\n",
			bpf_ntohl(pkt->itf_ipv4), bpf_ntohl(inner_dst_ip),
			ep->hosted_iface);

		bpf_debug("[Transit::0x%x] REDIRECT: {src=0x%x, dst=0x%x}/\n",
			  bpf_ntohl(pkt->itf_ipv4), bpf_ntohl(pkt->ip->saddr),
			  bpf_ntohl(pkt->ip->daddr));
		bpf_debug("[Transit::0x%x] REDIRECT: {vni:0x%x}/\n",
			  bpf_ntohl(pkt->itf_ipv4),
			  trn_vni_to_tunnel_id(pkt->geneve->vni));
		bpf_debug(
			"[Transit::0x%x] REDIRECT: {in.src=0x%x, in.dst=0x%x}\n",
			bpf_ntohl(pkt->itf_ipv4), bpf_ntohl(inner_src_ip),
			bpf_ntohl(inner_dst_ip));
		return trn_decapsulate_and_redirect(pkt, ep->hosted_iface);
	}

	if (ep->nremote_ips == 0) {
		bpf_debug(
			"[Transit:%d:] DROP (BUG): Misconfigured endpoint with zero remote_ips!\n",
			__LINE__);
		return XDP_DROP;
	}

	trn_set_src_dst_ip_csum(pkt, pkt->ip->daddr, ep->remote_ips[0]);
	bpf_debug("[Transit::0x%x] TX: {src=0x%x, dst=0x%x}/\n",
		  bpf_ntohl(pkt->itf_ipv4), bpf_ntohl(pkt->ip->saddr),
		  bpf_ntohl(pkt->ip->daddr));
	bpf_debug("[Transit::0x%x] TX: {vni:0x%x}/\n", bpf_ntohl(pkt->itf_ipv4),
		  trn_vni_to_tunnel_id(pkt->geneve->vni));
	bpf_debug("[Transit::0x%x] TX: {in.src=0x%x, in.dst=0x%x}\n",
		  bpf_ntohl(pkt->itf_ipv4), bpf_ntohl(inner_src_ip),
		  bpf_ntohl(inner_dst_ip));
	return trn_rewrite_remote_mac(pkt);
}

static __inline int trn_process_inner_ip(struct transit_packet *pkt)
{
	pkt->inner_ip = (void *)pkt->inner_eth + pkt->inner_eth_off;
	__u32 ipproto;

	if (pkt->inner_ip + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	ipproto = pkt->inner_ip->protocol;

	// TODO: switch parse inner UDP/TCP
	return trn_switch_handle_pkt(pkt, pkt->inner_ip->saddr,
				     pkt->inner_ip->daddr);
}

static __inline int trn_process_inner_arp(struct transit_packet *pkt)
{
	unsigned char *sha;
	unsigned char *tha = NULL;
	__u32 *sip, *tip;
	__u64 csum = 0;

	pkt->inner_arp = (void *)pkt->inner_eth + sizeof(*pkt->inner_eth);

	if (pkt->inner_arp + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	if (pkt->inner_arp->ar_pro != bpf_htons(ETH_P_IP) ||
	    pkt->inner_arp->ar_hrd != bpf_htons(ARPHRD_ETHER)) {
		bpf_debug("[Transit:%d:0x%x] DROP: ARP unsupported protocol"
			  " or Hardware type for inner packet!\n",
			  __LINE__, bpf_ntohl(pkt->itf_ipv4));
		return XDP_DROP;
	}

	if (pkt->inner_arp->ar_op != bpf_htons(ARPOP_REPLY) &&
	    pkt->inner_arp->ar_op != bpf_htons(ARPOP_REQUEST)) {
		bpf_debug(
			"[Transit:%d:0x%x] DROP:"
			"Only ARP REPLY and REQUEST are supported, received [0x%x]\n",
			pkt->inner_arp->ar_op);
		return XDP_DROP;
	}

	if ((unsigned char *)(pkt->inner_arp + 1) > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	sha = (unsigned char *)(pkt->inner_arp + 1);

	if (sha + ETH_ALEN > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	sip = (__u32 *)(sha + ETH_ALEN);

	if (sip + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	tha = (unsigned char *)sip + sizeof(__u32);

	if (tha + ETH_ALEN > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	tip = (__u32 *)(tha + ETH_ALEN);

	if ((void *)tip + sizeof(__u32) > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	__be64 tunnel_id = trn_vni_to_tunnel_id(pkt->geneve->vni);
	struct endpoint_t *ep;
	struct endpoint_key_t epkey;

	__builtin_memcpy(&epkey.tunip[0], &tunnel_id, sizeof(tunnel_id));
	epkey.tunip[2] = *tip;
	ep = bpf_map_lookup_elem(&endpoints_map, &epkey);

	if (ep && pkt->inner_arp->ar_op == bpf_htons(ARPOP_REQUEST)) {
		/* Respond to ARP */
		pkt->inner_arp->ar_op = bpf_htons(ARPOP_REPLY);
		trn_set_arp_ha(tha, sha);
		trn_set_arp_ha(sha, ep->mac);

		__u32 tmp_ip = *sip;
		*sip = *tip;
		*tip = tmp_ip;

		/* Set the sender mac address to the ep mac address */
		trn_set_src_mac(pkt->inner_eth, ep->mac);

		/* We need to lookup the endpoint again, since tip has changed */
		epkey.tunip[2] = *tip;
		ep = bpf_map_lookup_elem(&endpoints_map, &epkey);
	}

	return trn_switch_handle_pkt(pkt, *sip, *tip);
}

static __inline int trn_process_inner_eth(struct transit_packet *pkt)
{
	pkt->inner_eth = (void *)pkt->geneve + sizeof(*pkt->geneve);
	pkt->inner_eth_off = sizeof(*pkt->inner_eth);

	if (pkt->inner_eth + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	/* ARP */
	if (pkt->inner_eth->h_proto == bpf_htons(ETH_P_ARP)) {
		bpf_debug("[Transit:%d:0x%x] Processing ARP \n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return trn_process_inner_arp(pkt);
	}

	if (pkt->eth->h_proto != bpf_htons(ETH_P_IP)) {
		bpf_debug(
			"[Transit:%d:0x%x] DROP: unsupported inner packet: [0x%x]\n",
			__LINE__, bpf_ntohl(pkt->itf_ipv4),
			bpf_ntohs(pkt->eth->h_proto));
		return XDP_DROP;
	}

	bpf_debug("[Transit:%d:0x%x] Processing IP \n", __LINE__,
		  bpf_ntohl(pkt->itf_ipv4));
	return trn_process_inner_ip(pkt);
}

static __inline int trn_process_geneve(struct transit_packet *pkt)
{
	int opts_len;

	pkt->geneve = (void *)pkt->udp + sizeof(*pkt->udp);
	if (pkt->geneve + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	if (pkt->geneve->proto_type != bpf_htons(ETH_P_TEB)) {
		bpf_debug(
			"[Transit:%d:0x%x] PASS: unrecognized geneve proto_type: [0x%x]\n",
			__LINE__, bpf_ntohl(pkt->itf_ipv4),
			pkt->geneve->proto_type);
		return XDP_PASS;
	}

	opts_len = pkt->geneve->opt_len * 4;
	struct geneve_opt *opt = &pkt->geneve->options[0];

	if (opt + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	// TODO: process options

	return trn_process_inner_eth(pkt);
}

static __inline int trn_process_udp(struct transit_packet *pkt)
{
	/* Get the UDP header */
	pkt->udp = (void *)pkt->ip + sizeof(*pkt->ip);

	if (pkt->udp + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	if (pkt->udp->dest != GEN_DSTPORT) {
		bpf_debug("[Transit:%d:0x%x] PASS non-geneve packet \n",
			  __LINE__, bpf_ntohl(pkt->itf_ipv4));
		return XDP_PASS;
	}

	return trn_process_geneve(pkt);
}

static __inline int trn_process_ip(struct transit_packet *pkt)
{
	/* Get the IP header */
	pkt->ip = (void *)pkt->eth + pkt->eth_off;

	if (pkt->ip + 1 > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_ABORTED;
	}

	if (pkt->ip->protocol != IPPROTO_UDP) {
		bpf_debug("[Transit:%d:0x%x] PASS non-UDP packet \n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
		return XDP_PASS;
	}

	/* Only process packets designated to this interface!
	 * In functional tests - relying on docker0 - we see such packets!
	 */
	if (pkt->ip->daddr != pkt->itf_ipv4) {
		bpf_debug(
			"[Transit:%d:0x%x] DROP: packet dst address [0x%x] mismatch interface address.\n",
			__LINE__, bpf_ntohl(pkt->itf_ipv4),
			bpf_ntohl(pkt->ip->daddr));
		return XDP_DROP;
	}

	return trn_process_udp(pkt);
}

static __inline int trn_process_eth(struct transit_packet *pkt)
{
	pkt->eth = pkt->data;
	pkt->eth_off = sizeof(*pkt->eth);

	if (pkt->data + pkt->eth_off > pkt->data_end) {
		bpf_debug("[Transit:%d:0x%x] ABORTED: Bad offset\n", __LINE__,
			  bpf_ntohl(pkt->itf_ipv4));
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
	itf = bpf_map_lookup_elem(&interface_config_map, &k);

	if (!itf) {
		bpf_debug("[Transit:%d:] ABORTED: Bad configuration\n",
			  __LINE__);
		return XDP_ABORTED;
	}

	pkt.itf_ipv4 = itf->ip;
	pkt.itf_idx = itf->iface_index;

	int action = trn_process_eth(&pkt);

	/* The agent may tail-call this program, override XDP_TX to
	 * redirect to egress instead */
	if (action == XDP_TX)
		action = bpf_redirect(pkt.itf_idx, 0);

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

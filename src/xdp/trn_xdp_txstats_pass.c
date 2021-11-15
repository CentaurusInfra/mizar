// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_xdp_txstats_pass.c
 * @author Vinay Kulkarni (@vinaykul)
 *
 * @brief XDP statistics
 *
 * @copyright Copyright (c) 2021 The Authors.
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
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include "extern/bpf_endian.h"
#include "trn_xdp_stats_maps.h"
#include "trn_kern.h"

SEC("txstats_pass")
int _txstats(struct xdp_md *ctx)
{
	__u64 pkt_size = (__u64)(ctx->data_end - ctx->data);
	struct tx_stats_key_t txstatskey;
	__builtin_memset(&txstatskey, 0, sizeof(txstatskey));
	struct tx_stats_t *tx_stats = bpf_map_lookup_elem(&tx_stats_map, &txstatskey);
	if (tx_stats) {
		__sync_fetch_and_add(&tx_stats->tx_pkts_xdp_pass, 1);
		__sync_fetch_and_add(&tx_stats->tx_bytes_xdp_pass, pkt_size);

		void *data = (void *)(long)ctx->data;
		void *data_end = (void *)(long)ctx->data_end;
		struct ethhdr *eh = (void *)data;
		__u64 ehoff = sizeof(*eh);
		if (eh + 1 > data_end) {
			bpf_debug("[txstats_pass] Bad offset for eth header [%d]\n",
					__LINE__);
			return XDP_PASS;
		}
		if (eh->h_proto != bpf_htons(ETH_P_IP)) {
			bpf_debug("[txstats_pass] Not an IP packet\n");
			return XDP_PASS;
		}
		struct iphdr *iph = (void *)eh + ehoff;
		if (iph + 1 > data_end) {
			bpf_debug("[txstats_pass] Bad offset for ip header [%d]\n",
					__LINE__);
			return XDP_PASS;
		}
		__u8 dscp_code = iph->tos >> 2;
		if ((dscp_code == DSCP_EXPEDITED_HIGH) || (dscp_code == DSCP_EXPEDITED_MEDIUM) || (dscp_code == DSCP_EXPEDITED_LOW)) {
			__sync_fetch_and_add(&tx_stats->tx_pkts_xdp_expedited, 1);
			__sync_fetch_and_add(&tx_stats->tx_bytes_xdp_expedited, pkt_size);
		}
	}
	return XDP_PASS;
}

char _license[] SEC("license") = "GPL";

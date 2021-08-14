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
#include "trn_xdp_stats_maps.h"

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
	}
	return XDP_PASS;
}

char _license[] SEC("license") = "GPL";

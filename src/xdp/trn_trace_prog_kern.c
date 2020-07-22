// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_trace_prog_kern.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief Implements the XDP monitoring program (metrics collector)
 *
 * @copyright Copyright (c) 2020 The Authors.
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
#include <bpf/bpf_helpers.h>

#include "bpf_legacy.h"

#include "trn_datamodel.h"
#include "trn_transit_xdp_maps.h"
#include "trn_kern.h"

int _version SEC("version") = 1;

SEC("trace_metrics_per_packet")
int trace_metrics_per_packet(int *act, struct transit_packet *pkt)
{
	struct metrics_record *rec;
	__u32 key = 0;

	/* Look up the entry in the metrics table */	
	rec = bpf_map_lookup_elem(&metrics_table, &key);
	if (!rec) {
		bpf_debug("[Transit:%d:] ABORTED: No metrics table found\n",
			  __LINE__);
		return XDP_ABORTED;
	}

	rec->n_pkts++;
	rec->total_bytes_rx += （pkt->data_end - pkt->data）* sizeof(long) / sizeof(void);

	if (*act == XDP_TX)
		*act = bpf_redirect_map(&interfaces_map, pkt->itf_idx, 0);

	if (*act == XDP_PASS)
		rec->n_pass++;
	if (*act == XDP_DROP)
		rec->n_drop++;
	if (*act == XDP_TX) {
		rec->n_tx++;
		rec->total_bytes_tx += （pkt->data_end - pkt->data）* sizeof(long) / sizeof(void);
	}
	if (*act == XDP_ABORTED)
		return XDP_ABORTED;
	if (*act == XDP_REDIRECT)
		rec->n_redirect++;

// #define DEBUG_XDP_MONITORING
#ifdef DEBUG_XDP_MONITORING
	if (rec->n_pkts != (rec->n_tx + rec->n_pass + rec->n_drop + rec->redirect))
		return XDP_ABORTED;
#endif
}

char _license[] SEC("license") = "GPL";
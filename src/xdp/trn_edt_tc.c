// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_edt_tc.c
 * @author Vinay Kulkarni (@vinaykul)
 *
 * @brief EDT (Earliest Departure Time) rate-limiting eBFP program
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
#include <linux/bpf.h>
#include <linux/pkt_cls.h>
#include <linux/if_ether.h>
#include <linux/in.h>
#include <linux/ip.h>
#include <linux/udp.h>
#include <stdint.h>
#include "extern/bpf_endian.h"
#include "extern/bpf_helpers.h"
#include "src/include/trn_datamodel.h"
#include "src/xdp/trn_bw_qos_config_maps.h"
#include "trn_kern.h"

#define NSEC_PER_SEC    (1000ULL * 1000ULL * 1000UL)

// Optimization barrier. 'volatile' is due to gcc bugs
#ifndef barrier
#define barrier() 		__asm__ __volatile__("": : :"memory")
#endif

#ifndef __read_once
#define __read_once(x)		(*(volatile typeof(x) *)&x)
#endif

#ifndef __write_once
#define __write_once(x, v)	(*(volatile typeof(x) *)&x) = (v)
#endif

#ifndef read_once
#define read_once(x)						\
			({ typeof(x) _v = __read_once(x);	\
				barrier();			\
				_v;				\
			})
#endif

#ifndef write_once
#define write_once(x, v)					\
			({ typeof(x) _v = (v);			\
				__write_once(x, _v);		\
				barrier();			\
				_v;				\
			})
#endif


static __ALWAYS_INLINE__ int edt_schedule_departure(struct __sk_buff *skb, __u32 saddr)
{
	struct bw_qos_config_key_t key;
	struct bw_qos_config_t *ec;
	__u64 delay = 0, now = 0, t = 0, t_next = 0;
	char ec_null_msg[] = "ERR: EDT map not found. saddr=0x%x if_index=%d\n";
	char ec_ts_msg[] = "EVAL tlast=%llu now=%llu tstamp=%llu\n";
	char ec_ts_set_msg[] = "SET now=%llu dlay=%llu tnxt=%llu\n";
	char ec_ts_drop_msg[] = "*DROP* now=%llu dlay=%llu tnxt=%llu\n";

	key.saddr = saddr;
	ec = (struct bw_qos_config_t *)bpf_map_lookup_elem(&bw_qos_config_map, &key);
	if (!ec) {
		bpf_trace_printk(ec_null_msg, sizeof(ec_null_msg), key.saddr, skb->ifindex);
		return TC_ACT_OK;
	}

	now = bpf_ktime_get_ns();

	t = skb->tstamp;
	bpf_trace_printk(ec_ts_msg, sizeof(ec_ts_msg), ec->t_last, now, t);
	if (t < now) {
		t = now;
	}
	delay = (skb->wire_len) * NSEC_PER_SEC / ec->egress_bandwidth_bytes_per_sec;
	t_next = read_once(ec->t_last) + delay;
	if (t_next <= t) {
		write_once(ec->t_last, t);
		return TC_ACT_OK;
	}

	if (t_next - now >= ec->t_horizon_drop) {
		bpf_trace_printk(ec_ts_drop_msg, sizeof(ec_ts_drop_msg), now, delay, t_next);
		return TC_ACT_SHOT;
	}
	write_once(ec->t_last, t_next);

	bpf_trace_printk(ec_ts_set_msg, sizeof(ec_ts_set_msg), now, delay, t_next);
	skb->tstamp = t_next;
	return TC_ACT_OK;
}

SEC("edt")
int tc_edt(struct __sk_buff *skb)
{
	//
	// Set skb->tstamp to enforce EDT rate limiting
	//
	int rc = TC_ACT_OK;
	char in_msg[] = "=====>>>>\n";
	char out_msg[] = "<<<<===== [TC_Action: %d]\n";
	char edt_msg[] = "[TC-EDT:0x%x] Low priority packet Dst: 0x%x\n";
	void *data = (void *)(long)skb->data;
	void *data_end = (void *)(long)skb->data_end;

	if (data + sizeof(struct ethhdr) + sizeof(struct iphdr) + sizeof(struct udphdr) < data_end) {
		struct ethhdr *eth = data;
		struct iphdr *ip = (data + sizeof(struct ethhdr));
		// Enforce EDT only for GENEVE frames classified as BestEffort Low priority
		if (ip->protocol == IPPROTO_UDP) {
			struct udphdr *udp = (data + sizeof(struct ethhdr) + sizeof(struct iphdr));
			__u8 dscp_code = ip->tos >> 2;
			if ((udp->dest == GEN_DSTPORT) &&
				((dscp_code == DSCP_BESTEFFORT_HIGH) || (dscp_code == DSCP_BESTEFFORT_MEDIUM) || (dscp_code == DSCP_BESTEFFORT_LOW))) {
				bpf_trace_printk(in_msg, sizeof(in_msg));
				bpf_trace_printk(edt_msg, sizeof(edt_msg), bpf_ntohl(ip->saddr),
							bpf_ntohl(ip->daddr), udp->source);
				rc = edt_schedule_departure(skb, bpf_ntohl(ip->saddr));
				bpf_trace_printk(out_msg, sizeof(out_msg), rc);
			}
		}
	}
	return rc;
}

char __license[] SEC("license") = "GPL";

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
#include "trn_kern.h"

#define LOWBPS          (20UL)
#define ONEKBPS         (1000UL)
#define TENKBPS         (1000UL * 10)
#define HUNDREDKBPS     (1000ULL * 100ULL)
#define ONEMBPS         (1000000ULL)
#define NSEC_PER_SEC    (1000ULL * 1000ULL * 1000UL)
#define NSEC_PER_MSEC   (1000ULL * 1000ULL)
#define NSEC_PER_USEC   (1000UL)

#ifndef __section
#define __section(NAME)                  \
	__attribute__((section(NAME), used))
#endif

#ifndef barrier
#define barrier()		asm volatile("": : :"memory")
#endif

#ifndef __READ_ONCE
#define __READ_ONCE(X)		(*(volatile typeof(X) *)&X)
#endif

#ifndef __WRITE_ONCE
#define __WRITE_ONCE(X, V)	(*(volatile typeof(X) *)&X) = (V)
#endif

/* {READ,WRITE}_ONCE() with verifier workaround via bpf_barrier(). */
#ifndef READ_ONCE
#define READ_ONCE(X)						\
			({ typeof(X) __val = __READ_ONCE(X);	\
				barrier();			\
				 __val; })
#endif

#ifndef WRITE_ONCE
#define WRITE_ONCE(X, V)					\
			({ typeof(X) __val = (V);		\
				__WRITE_ONCE(X, __val);		\
				barrier();			\
				__val; })
#endif


struct edt_info {
    __u64 bps;
    __u64 t_last;
    __u64 t_horizon_drop;
};

struct bpf_map_def SEC("maps") THROTTLE_MAP = {
    .type        = BPF_MAP_TYPE_HASH,
    .key_size    = sizeof(int),
    .value_size  = sizeof(struct edt_info),
    .max_entries = 1,
    .map_flags   = 0,
};

int edt_schedule_departure(struct __sk_buff *skb)
{
	int key = 0;
	struct edt_info *einfo;
	__u64 delay = 0, now = 0, t = 0, t_next = 0;
	char einfo_null_msg[] = "ERR: Map not found\n";
	char einfo_ts_msg[] = "EVAL tlast=%llu now=%llu tstamp=%llu\n";
	char einfo_ts_set_msg[] = "SET now=%llu dlay=%llu tnxt=%llu\n";
	char einfo_ts_drop_msg[] = "*DROP* now=%llu dlay=%llu tnxt=%llu\n";

	einfo = (struct edt_info *)bpf_map_lookup_elem(&THROTTLE_MAP, &key);
	if (!einfo) {
		bpf_trace_printk(einfo_null_msg, sizeof(einfo_null_msg));
		return TC_ACT_OK;
	}

	now = bpf_ktime_get_ns();

	t = skb->tstamp;
	bpf_trace_printk(einfo_ts_msg, sizeof(einfo_ts_msg), einfo->t_last, now, t);
	if (t < now) {
		t = now;
	}
	delay = (skb->wire_len) * NSEC_PER_SEC / einfo->bps;
	t_next = READ_ONCE(einfo->t_last) + delay;
	if (t_next <= t) {
		WRITE_ONCE(einfo->t_last, t);
		return TC_ACT_OK;
	}

	/* FQ implements a drop horizon, see also 39d010504e6b ("net_sched:
	 * sch_fq: add horizon attribute"). However, we explicitly need the
	 * drop horizon here to i) avoid having t_last messed up and ii) to
	 * potentially allow for per aggregate control.
	 */
	if (t_next - now >= einfo->t_horizon_drop) {
		bpf_trace_printk(einfo_ts_drop_msg, sizeof(einfo_ts_drop_msg), now, delay, t_next);
		return TC_ACT_SHOT;
	}
	WRITE_ONCE(einfo->t_last, t_next);

	bpf_trace_printk(einfo_ts_set_msg, sizeof(einfo_ts_set_msg), now, delay, t_next);
	skb->tstamp = t_next;
	return TC_ACT_OK;
}

__section("edt")
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

	//TODO: User creates this map
	int key = 0;
	struct edt_info einfo = {};
	if (!bpf_map_lookup_elem(&THROTTLE_MAP, &key)) {
		//einfo.bps = LOWBPS;
		//einfo.bps = 2 * HUNDREDKBPS;
		einfo.bps = 6 * ONEKBPS;
		einfo.t_last = 0;
		einfo.t_horizon_drop = 2 * NSEC_PER_SEC;
		bpf_map_update_elem(&THROTTLE_MAP, &key, &einfo, BPF_NOEXIST);
	}

	if (data + sizeof(struct ethhdr) + sizeof(struct iphdr) + sizeof(struct udphdr) < data_end) {
		struct ethhdr *eth = data;
		struct iphdr *ip = (data + sizeof(struct ethhdr));
		// Enforce EDT only for GENEVE frames classified as MINCOST
		if (ip->protocol == IPPROTO_UDP) {
			struct udphdr *udp = (data + sizeof(struct ethhdr) + sizeof(struct iphdr));
			if ((udp->dest == GEN_DSTPORT) && (ip->tos & IPTOS_MINCOST)) {
				bpf_trace_printk(in_msg, sizeof(in_msg));
				bpf_trace_printk(edt_msg, sizeof(edt_msg), ip->saddr, ip->daddr, udp->source);
				rc = edt_schedule_departure(skb);
				bpf_trace_printk(out_msg, sizeof(out_msg), rc);
			}
		}
	}
	return rc;
}

char __license[] __section("license") = "GPL";

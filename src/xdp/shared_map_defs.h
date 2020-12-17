#pragma once

#include <linux/bpf.h>

#include "extern/bpf_helpers.h"
#include "extern/xdpcap_hook.h"

#include "trn_datamodel.h"

// common map definitions for network policy check;
// they are shared acrossed ingress and egress XDP prog

// for egress policies
struct bpf_map_def SEC("maps") eg_vsip_enforce_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct vsip_enforce_t),
	.value_size = sizeof(__u8),
	.max_entries = 1024,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(eg_vsip_enforce_map, struct vsip_enforce_t, __u8);

struct bpf_map_def SEC("maps") eg_vsip_prim_map = {
	.type = BPF_MAP_TYPE_LPM_TRIE,
	.key_size = sizeof(struct vsip_cidr_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 1,
};
BPF_ANNOTATE_KV_PAIR(eg_vsip_prim_map, struct vsip_cidr_t, __u64);

struct bpf_map_def SEC("maps") eg_vsip_ppo_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct vsip_ppo_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(eg_vsip_ppo_map, struct vsip_ppo_t, __u64);

struct bpf_map_def SEC("maps") eg_vsip_supp_map = {
	.type = BPF_MAP_TYPE_LPM_TRIE,
	.key_size = sizeof(struct vsip_cidr_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 1,
};
BPF_ANNOTATE_KV_PAIR(eg_vsip_supp_map, struct vsip_cidr_t, __u64);

struct bpf_map_def SEC("maps") eg_vsip_except_map = {
	.type = BPF_MAP_TYPE_LPM_TRIE,
	.key_size = sizeof(struct vsip_cidr_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 1,
};
BPF_ANNOTATE_KV_PAIR(eg_vsip_except_map, struct vsip_cidr_t, __u64);

// for ingress policies
struct bpf_map_def SEC("maps") ing_vsip_enforce_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct vsip_enforce_t),
	.value_size = sizeof(__u8),
	.max_entries = 1024,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(ing_vsip_enforce_map, struct vsip_enforce_t, __u8);

struct bpf_map_def SEC("maps") ing_vsip_prim_map = {
	.type = BPF_MAP_TYPE_LPM_TRIE,
	.key_size = sizeof(struct vsip_cidr_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 1,
};
BPF_ANNOTATE_KV_PAIR(ing_vsip_prim_map, struct vsip_cidr_t, __u64);

struct bpf_map_def SEC("maps") ing_vsip_ppo_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct vsip_ppo_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(ing_vsip_ppo_map, struct vsip_ppo_t, __u64);

struct bpf_map_def SEC("maps") ing_vsip_supp_map = {
	.type = BPF_MAP_TYPE_LPM_TRIE,
	.key_size = sizeof(struct vsip_cidr_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 1,
};
BPF_ANNOTATE_KV_PAIR(ing_vsip_supp_map, struct vsip_cidr_t, __u64);

struct bpf_map_def SEC("maps") ing_vsip_except_map = {
	.type = BPF_MAP_TYPE_LPM_TRIE,
	.key_size = sizeof(struct vsip_cidr_t),
	.value_size = sizeof(__u64),
	.max_entries = 1024 * 1024,
	.map_flags = 1,
};
BPF_ANNOTATE_KV_PAIR(ing_vsip_except_map, struct vsip_cidr_t, __u64);

// the global connection track map
struct bpf_map_def SEC("maps") conn_track_cache = {
	.type = BPF_MAP_TYPE_LRU_HASH,
	.key_size = sizeof(struct ipv4_ct_tuple_t),
	.value_size = sizeof(__u8),
	.max_entries = TRAN_MAX_CACHE_SIZE,
};
BPF_ANNOTATE_KV_PAIR(conn_track_cache, struct ipv4_ct_tuple_t, __u8);

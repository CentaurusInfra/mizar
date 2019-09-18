// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file transit_maps.h
 * @author Sherif Abdelwahab (@zasherif)
 *
 * @brief Defines ebpf maps of transit XDP
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
#pragma once

#include <linux/bpf.h>

#include "extern/bpf_helpers.h"
#include "extern/xdpcap_hook.h"

#include "trn_datamodel.h"

#define MAX_NETS 16385
#define MAX_EP 65537
#define MAX_VPC 8192

struct bpf_map_def SEC("maps") networks_map = {
	.type = BPF_MAP_TYPE_LPM_TRIE,
	.key_size = sizeof(struct network_key_t),
	.value_size = sizeof(struct network_t),
	.max_entries = MAX_NETS,
	.map_flags = BPF_F_NO_PREALLOC,
};
BPF_ANNOTATE_KV_PAIR(networks_map, struct network_key_t, struct network_t);

struct bpf_map_def SEC("maps") vpc_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct vpc_key_t),
	.value_size = sizeof(struct vpc_t),
	.max_entries = MAX_VPC,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(vpc_map, struct vpc_key_t, struct vpc_t);

struct bpf_map_def SEC("maps") endpoints_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct endpoint_key_t),
	.value_size = sizeof(struct endpoint_t),
	.max_entries = MAX_EP,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(endpoints_map, struct endpoint_key_t, struct endpoint_t);

struct bpf_map_def SEC("maps") hosted_endpoints_iface_map = {
	.type = BPF_MAP_TYPE_HASH,
	.key_size = sizeof(struct endpoint_key_t),
	.value_size = sizeof(int),
	.max_entries = MAX_EP,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(hosted_endpoints_iface_map, struct endpoint_key_t, int);

struct bpf_map_def SEC("maps") interface_config_map = {
	.type = BPF_MAP_TYPE_ARRAY,
	.key_size = sizeof(int),
	.value_size = sizeof(struct tunnel_iface_t),
	.max_entries = 1,
	.map_flags = 0,
};
BPF_ANNOTATE_KV_PAIR(interface_config_map, int, struct tunnel_iface_t);

struct bpf_map_def SEC("maps") xdpcap_hook = XDPCAP_HOOK();

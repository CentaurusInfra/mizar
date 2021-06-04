// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_edt_tc_maps.h
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

#pragma once

#include <linux/bpf.h>
#include "extern/bpf_helpers.h"
#include "trn_datamodel.h"

// TC eBPF EDT configuration map
struct bpf_map_def SEC("maps") edt_config_map = {
    .type        = BPF_MAP_TYPE_HASH,
    .key_size    = sizeof(unsigned int),
    .value_size  = sizeof(struct edt_config_t),
    .max_entries = 1,
    .map_flags   = 0,
};
BPF_ANNOTATE_KV_PAIR(edt_config_map, struct edt_config_t, __u64);

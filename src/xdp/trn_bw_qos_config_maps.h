// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_bw_qos_config_maps.h
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
#include "extern/bpf_elf.h"
#include "extern/bpf_helpers.h"
#include "trn_datamodel.h"

// TC eBPF Bandwidth QoS configuration map
struct bpf_elf_map SEC("maps") bw_qos_config_map = {
    .type        = BPF_MAP_TYPE_HASH,
    .size_key    = sizeof(struct bw_qos_config_key_t),
    .size_value  = sizeof(struct bw_qos_config_t),
    .max_elem    = 1,
    .pinning     = PIN_GLOBAL_NS,
};

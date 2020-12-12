// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file conntrack_common.h
 * @author Hongwei Chen (@hong.chen@futurewei.com)
 *
 * @brief Defines common code used in conntrack feature
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
#pragma once

#include "trn_kern.h"

__ALWAYS_INLINE__
static inline int conntrack_insert_tcpudp_conn(void *conntracks, __u64 tunnel_id, const struct ipv4_tuple_t *tuple)
{
	struct ipv4_ct_tuple_t conn = {
		.vpc.tunnel_id = tunnel_id,
		.tuple = *tuple,
	};
	__u8 value = 1;
	return (tuple->protocol == IPPROTO_TCP || tuple->protocol == IPPROTO_UDP) ?
		bpf_map_update_elem(conntracks, &conn, &value, 0) : 0;
}


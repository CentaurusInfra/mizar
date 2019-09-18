// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file datamodel.h
 * @author Sherif Abdelwahab (@zasherif)
 *
 * @brief Data models between user and kernel space. data propagated
 * from control-plane through transitd.
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

#include <linux/types.h>
#define __ALIGNED_64__ __attribute__((aligned(64)))
#define __ALWAYS_INLINE__ __attribute__((__always_inline__))

#define TRAN_MAX_NEP 65537
#define TRAN_MAX_NSWITCH 32768
#define TRAN_MAX_NROUTER 16384
#define TRAN_MAX_REMOTES 256

#define TRAN_SUBSTRT_VNI 0

#define TRAN_SUBSTRT_EP 0
#define TRAN_SIMPLE_EP 1

/* XDP programs keys */
#define XDP_TRANSIT 0

struct endpoint_key_t {
	__u32 tunip[3];
};

struct endpoint_t {
	__u32 eptype;
	__u32 nremote_ips;
	__u32 remote_ips[TRAN_MAX_REMOTES];
	int hosted_iface;
	unsigned char mac[6];
};

struct network_key_t {
	__u32 prefixlen; /* up to 32 for AF_INET, 128 for AF_INET6*/
	__u32 nip[3];
};

struct network_t {
	__u32 prefixlen; /* up to 32 for AF_INET, 128 for AF_INET6 */
	__u32 nip[3];
	__u32 nswitches;
	__u32 switches_ips[TRAN_MAX_NSWITCH];
};

struct vpc_key_t {
	union {
		__be64 tunnel_id;
	};
};

struct vpc_t {
	__u32 nrouters;
	__u32 routers_ips[TRAN_MAX_NROUTER];
};

struct tunnel_iface_t {
	int iface_index;
	__u32 ip;
	unsigned char mac[6];
};

struct agent_metadata_t {
	struct tunnel_iface_t eth;
	struct network_key_t nkey;
	struct network_t net;
	struct endpoint_key_t epkey;
	struct endpoint_t ep;
};
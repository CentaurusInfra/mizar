// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_trace_prog_usr.c
 * @author ShixiongQi (@ShixiongQi)
 *		   Sherif Abdelwahab (@zasherif)
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

#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/err.h>
#include <linux/kernel.h>
#include <net/if.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

#include <bpf/bpf.h>
#include <bpf/btf.h>

#define EXIT_OK 		    0
#define EXIT_FAIL		    1
#define EXIT_FAIL_BPF		40

/* Look up the file descriptor of the eBPF map based on map name */
static int do_bpf_map_lookup_fd(char *name, struct bpf_map *map);

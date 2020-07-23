// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_trace_prog_usr.c
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <getopt.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <net/if.h>

#include <locale.h>
#include <unistd.h>
#include <time.h>

#include <bpf/bpf.h>
#include <bpf/libbpf.h>

#include <net/if.h>
#include <linux/if_link.h> /* depend on kernel-headers installed */

#include <linux/err.h>

#include "../common/common_params.h"
#include "../common/common_user_bpf_xdp.h"
#include "../common/common_libbpf.h"
#include "bpf_util.h" /* bpf_num_possible_cpus */

#include <linux/perf_event.h>
#define _GNU_SOURCE         /* See feature_test_macros(7) */
#include <unistd.h>
#include <sys/syscall.h>   /* For SYS_xxx definitions */
#include <sys/ioctl.h>

#include "trn_datamodel.h"

/* struct metrics_record defined in trn_datamodel.h */

/* Userspace structs for collection of stats from maps */
struct record {
	__u64 timestamp;
	struct metrics_record total;
	struct metrics_record *cpu;
};

struct stats_record {
	struct record xdp_cpumap_net_stats;
};

static int __check_map_fd_info(int map_fd, struct bpf_map_info *info,
			       struct bpf_map_info *exp)
{
	__u32 info_len = sizeof(*info);
	int err;

	if (map_fd < 0)
		return EXIT_FAIL;

        /* BPF-info via bpf-syscall */
	err = bpf_obj_get_info_by_fd(map_fd, info, &info_len);
	if (err) {
		fprintf(stderr, "ERR: %s() can't get info - %s\n",
			__func__,  strerror(errno));
		return EXIT_FAIL_BPF;
	}

	if (exp->key_size && exp->key_size != info->key_size) {
		fprintf(stderr, "ERR: %s() "
			"Map key size(%d) mismatch expected size(%d)\n",
			__func__, info->key_size, exp->key_size);
		return EXIT_FAIL;
	}
	if (exp->value_size && exp->value_size != info->value_size) {
		fprintf(stderr, "ERR: %s() "
			"Map value size(%d) mismatch expected size(%d)\n",
			__func__, info->value_size, exp->value_size);
		return EXIT_FAIL;
	}
	if (exp->max_entries && exp->max_entries != info->max_entries) {
		fprintf(stderr, "ERR: %s() "
			"Map max_entries(%d) mismatch expected size(%d)\n",
			__func__, info->max_entries, exp->max_entries);
		return EXIT_FAIL;
	}
	if (exp->type && exp->type  != info->type) {
		fprintf(stderr, "ERR: %s() "
			"Map type(%d) mismatch expected type(%d)\n",
			__func__, info->type, exp->type);
		return EXIT_FAIL;
	}

	return 0;
}

static int __check_map(int map_fd, struct bpf_map_info *exp)
{
	struct bpf_map_info info;

	return __check_map_fd_info(map_fd, &info, exp);
}

static int check_map(const char *name, const struct bpf_map_def *def, int fd)
{
	struct {
		const char          *name;
		struct bpf_map_info  info;
	} maps[] = {
		{
			.name = "metrics_table",
			.info = {
				.type = BPF_MAP_TYPE_PERCPU_ARRAY,
				.key_size = sizeof(__u32),
				.value_size = sizeof(struct metrics_record),
				.max_entries = 1,
			}
		},
		{ }
	};
	int i = 0;

	fprintf(stdout, "checking map %s\n", name);

	while (maps[i].name) {
		if (!strcmp(maps[i].name, name))
			return __check_map(fd, &maps[i].info);
		i++;
	}

	fprintf(stdout, "ERR: map %s not found\n", name);
	return -1;
}

static int check_maps(struct bpf_map *map)
{
	// struct bpf_map *map;

	// bpf_object__for_each_map(map, obj) {
	const struct bpf_map_def *def;
	const char *name;
	int fd;

	name = bpf_map__name(map);
	def  = bpf_map__def(map);
	fd   = bpf_map__fd(map);

	if (check_map(name, def, fd)) /* if map exists, return 0 */
		return -1;
	// }
	/* return 0 on successful maps check */
	return 0;
}

#define NANOSEC_PER_SEC 1000000000 /* 10^9 */
static __u64 gettime(void)
{
	struct timespec t;
	int res;

	res = clock_gettime(CLOCK_MONOTONIC, &t);
	if (res < 0) {
		fprintf(stderr, "Error with gettimeofday! (%i)\n", res);
		exit(-1);
	}
	return (__u64) t.tv_sec * NANOSEC_PER_SEC + t.tv_nsec;
}

static bool map_collect_record(int fd, __u32 key, struct record *rec)
{
	/* For percpu maps, userspace gets a value per possible CPU */
	unsigned int nr_cpus = bpf_num_possible_cpus();
	struct metrics_record values[nr_cpus];
	__u64 sum_n_pkts = 0;
	__u64 sum_total_bytes_rx = 0;
	__u64 sum_total_bytes_tx = 0;
	__u64 sum_n_tx = 0;
	__u64 sum_n_pass = 0;
	__u64 sum_n_drop = 0;
	__u64 sum_n_redirect = 0;
	int i;

	if ((bpf_map_lookup_elem(fd, &key, values)) != 0) {
		fprintf(stderr,
			"ERR: bpf_map_lookup_elem failed key:0x%X\n", key);
		return false;
	}
	/* Get time as close as possible to reading map contents */
	rec->timestamp = gettime();

	/* Record and sum values from each CPU */
	for (i = 0; i < nr_cpus; i++) {
		rec->cpu[i].n_pkts         =  values[i].n_pkts;
		sum_n_pkts                 += values[i].n_pkts;
		rec->cpu[i].total_bytes_rx =  values[i].total_bytes_rx;
		sum_total_bytes_rx         += values[i].total_bytes_rx;
		rec->cpu[i].total_bytes_tx =  values[i].total_bytes_tx;
		sum_total_bytes_tx         += values[i].total_bytes_tx;
		rec->cpu[i].n_tx           =  values[i].n_tx;
		sum_n_tx                   += values[i].n_tx;
		rec->cpu[i].n_pass         =  values[i].n_pass;
		sum_n_pass                 += values[i].n_pass;
		rec->cpu[i].n_drop         =  values[i].n_drop;
		sum_n_drop                 += values[i].n_drop;
		rec->cpu[i].n_redirect     =  values[i].n_redirect;
		sum_n_redirect             += values[i].n_redirect;

	}
	rec->total.n_pkts         = sum_n_pkts;
	rec->total.total_bytes_rx = sum_total_bytes_rx;
	rec->total.total_bytes_tx = sum_total_bytes_tx;
	rec->total.n_tx           = sum_n_tx;
	rec->total.n_pass         = sum_n_pass;
	rec->total.n_drop         = sum_n_drop;
	rec->total.n_redirect     = sum_n_redirect;

	return true;
}

static double calc_period(struct record *r, struct record *p)
{
	double period_ = 0;
	__u64 period = 0;

	period = r->timestamp - p->timestamp;
	if (period > 0)
		period_ = ((double) period / NANOSEC_PER_SEC);

	return period_;
}

static double calc_rx_pps(struct metrics_record *r, struct metrics_record *p, double period)
{
	__u64 packets = 0;
	double pps = 0;

	if (period > 0) {
		packets = r->n_pkts - p->n_pkts;
		pps = packets / period;
	}
	return pps;
}

static double calc_tx_pps(struct metrics_record *r, struct metrics_record *p, double period)
{
	__u64 packets = 0;
	double pps = 0;

	if (period > 0) {
		packets = r->n_tx - p->n_tx;
		pps = packets / period;
	}
	return pps;
}

//TODO: the calc_ functions for the metrics we collect from kernel
static int calc_n_pkts(struct metrics_record *r, struct metrics_record *p, double period);

static int calc_total_bytes_rx(struct metrics_record *r, struct metrics_record *p, double period);

static int calc_total_bytes_tx(struct metrics_record *r, struct metrics_record *p, double period);

static int calc_n_tx(struct metrics_record *r, struct metrics_record *p, double period);

static int calc_n_pass(struct metrics_record *r, struct metrics_record *p, double period);

static int calc_n_drop(struct metrics_record *r, struct metrics_record *p, double period);

static int calc_n_redirect(struct metrics_record *r, struct metrics_record *p, double period);

//TODO: build stats_prints
// static void stats_print(struct stats_record *stats_rec,
// 			struct stats_record *stats_prev,
// 			bool err_only)
// {
// 	unsigned int nr_cpus = bpf_num_possible_cpus();
// 	int rec_i = 0, i;
// 	double t = 0, pps = 0;

// 	/* Header */
// 	printf("%-15s %-7s %-12s %-12s %-9s\n",
// 	       "XDP-event", "CPU:to", "pps", "drop-pps", "extra-info");


// 	/* network stats on Transit XDP program (Or we call it bouncer / divider ?) */
// 	// for (to_cpu = 0; to_cpu < MAX_CPUS; to_cpu++) {
// 	char *fmt1 = "%-15s %3d:%-3d %'-12.0f %'-12.0f %'-10.2f %s\n";
// 	char *fmt2 = "%-15s %3s:%-3d %'-12.0f %'-12.0f %'-10.2f %s\n";
// 	struct record *rec, *prev;
// 	char *info_str = "";
// 	double drop, info;

// 	rec  =  &stats_rec->xdp_cpumap_net_stats;
// 	prev = &stats_prev->xdp_cpumap_net_stats;
// 	t = calc_period(rec, prev);
// 	for (i = 0; i < nr_cpus; i++) {
// 		struct metrics_record *r = &rec->cpu[i];
// 		struct metrics_record *p = &prev->cpu[i];

// 		pps  = calc_pps(r, p, t);
// 		drop = calc_drop(r, p, t);
// 		info = calc_info(r, p, t);
// 		if (info > 0) {
// 			info_str = "bulk-average";
// 			info = pps / info; /* calc average bulk size */
// 		}
// 		if (pps > 0)
// 			printf(fmt1, "cpumap-enqueue",
// 			       i, to_cpu, pps, drop, info, info_str);
// 	}
// 	pps = calc_pps(&rec->total, &prev->total, t);
// 	if (pps > 0) {
// 		drop = calc_drop(&rec->total, &prev->total, t);
// 		info = calc_info(&rec->total, &prev->total, t);
// 		if (info > 0) {
// 			info_str = "bulk-average";
// 			info = pps / info; /* calc average bulk size */
// 		}
// 		printf(fmt2, "cpumap-enqueue",
// 		       "sum", to_cpu, pps, drop, info, info_str);
// 	}
// 	// }

// 	printf("\n");
// }

static bool stats_collect(struct bpf_map *map, struct stats_record *rec)
{
	int fd;
	int i;

	// Get the fd of bpf map
	fd = bpf_map__fd(map);
	map_collect_record(fd, i, &rec->xdp_cpumap_net_stats);

	return true;
}

static void *alloc_rec_per_cpu(int record_size)
{
	unsigned int nr_cpus = bpf_num_possible_cpus();
	void *array;
	size_t size;

	size = record_size * nr_cpus;
	array = malloc(size);
	memset(array, 0, size);
	if (!array) {
		fprintf(stderr, "Mem alloc error (nr_cpus:%u)\n", nr_cpus);
		exit(-1);
	}
	return array;
}

static struct stats_record *alloc_stats_record(void)
{
	struct stats_record *rec;
	int rec_sz;

	/* Alloc main stats_record structure */
	rec = malloc(sizeof(*rec));
	memset(rec, 0, sizeof(*rec));
	if (!rec) {
		fprintf(stderr, "Mem alloc error\n");
		exit(-1);
	}

	/* Alloc stats stored per CPU for each record */
	rec_sz = sizeof(struct metrics_record);
	rec->xdp_cpumap_net_stats.cpu = alloc_rec_per_cpu(rec_sz);

	return rec;
}

static void free_stats_record(struct stats_record *r)
{
	free(r->xdp_cpumap_net_stats.cpu);
	free(r);
}

/* Pointer swap trick */
static inline void swap(struct stats_record **a, struct stats_record **b)
{
	struct stats_record *tmp;

	tmp = *a;
	*a = *b;
	*b = tmp;
}

static void stats_poll(struct bpf_map *map, int interval, bool err_only)
{
	struct stats_record *rec, *prev;

	rec  = alloc_stats_record();
	prev = alloc_stats_record();
	stats_collect(map, rec);

	if (err_only)
		printf("\n%s\n", "???");

	/* Trick to pretty printf with thousands separators use %' */
	setlocale(LC_NUMERIC, "en_US");

	while (1) {
		swap(&prev, &rec);
		stats_collect(map, rec);
		stats_print(rec, prev, err_only);
		fflush(stdout);
		sleep(interval);
	}

	free_stats_record(rec);
	free_stats_record(prev);
}

int main(int argc, char **argv)
{
	struct bpf_map *map;
	int interval = 2; /* sampling interval */
	const char *bpf_map_name = "metrics_table";

	map = (struct bpf_map*)malloc(sizeof(struct bpf_map));
	map->name = bpf_map_name;
	// where to find the file descriptor. It should belong to the bpf program running in transit xdp
	// TODO: Find a way to get the fd, it is also needed in the stats_poll().
	map->fd = 1;
	map->def = NULL;

	if (check_maps(map))
		return EXIT_FAIL_BPF;

	// TODO: replace bpf_obj with struct bpf_map *map
	// but we need to get the fd of the map in advance,
	// all the following metrics collecting operations
	// are based on the fd of map.
	stats_poll(map, interval, false);
	return EXIT_OK;
}

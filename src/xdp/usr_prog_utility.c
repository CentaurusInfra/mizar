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

static int map_fd_by_name(char *name, int **fds)
{
	unsigned int id = 0;
	int fd, nb_fds = 0;
	void *tmp;
	int err;

	while (true) {
		struct bpf_map_info info = {};
		__u32 len = sizeof(info);

		err = bpf_map_get_next_id(id, &id);
		if (err) {
			if (errno != ENOENT) {
				p_err("%s", strerror(errno));
				goto err_close_fds;
			}
			return nb_fds;
		}

		fd = bpf_map_get_fd_by_id(id);
		if (fd < 0) {
			p_err("can't get map by id (%u): %s",
			      id, strerror(errno));
			goto err_close_fds;
		}

		err = bpf_obj_get_info_by_fd(fd, &info, &len);
		if (err) {
			p_err("can't get map info (%u): %s",
			      id, strerror(errno));
			goto err_close_fd;
		}

		if (strncmp(name, info.name, BPF_OBJ_NAME_LEN)) {
			close(fd);
			continue;
		}

		if (nb_fds > 0) {
			tmp = realloc(*fds, (nb_fds + 1) * sizeof(int));
			if (!tmp) {
				p_err("failed to realloc");
				goto err_close_fd;
			}
			*fds = tmp;
		}
		(*fds)[nb_fds++] = fd;
	}

err_close_fd:
	close(fd);
err_close_fds:
	while (--nb_fds >= 0)
		close((*fds)[nb_fds]);
	return -1;
}

static int map_parse_fds(char *name, int **fds)
{
	if (strlen(name) > BPF_OBJ_NAME_LEN - 1) {
		p_err("can't parse name");
		return -1;
	}

	return map_fd_by_name(name, fds);
}

int map_parse_fd(char *name)
{
	int *fds = NULL;
	int nb_fds, fd;

	fds = malloc(sizeof(int));
	if (!fds) {
		p_err("mem alloc failed");
		return -1;
	}
	nb_fds = map_parse_fds(name, &fds);
	if (nb_fds != 1) {
		if (nb_fds > 1) {
			p_err("several maps match this handle");
			while (nb_fds--)
				close(fds[nb_fds]);
		}
		fd = -1;
		goto exit_free;
	}

	fd = fds[0];
exit_free:
	free(fds);
	return fd;
}

int map_parse_fd_and_info(char *name, void *info, __u32 *info_len)
{
	int err;
	int fd;

	fd = map_parse_fd(name);
	if (fd < 0)
		return -1;

	err = bpf_obj_get_info_by_fd(fd, info, info_len);
	if (err) {
		p_err("can't get map info: %s", strerror(errno));
		close(fd);
		return err;
	}

	return fd;
}

static int do_bpf_map_lookup_fd(char *name, struct bpf_map *map)
{
	struct bpf_map_info info = {};
	__u32 len = sizeof(info);

	map->fd = map_parse_fd_and_info(name, &info, &len);
	if (map->fd < 0)
		return -1;

	return 1;
}

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

static int map_parse_fds(int *argc, char ***argv, int **fds)
{
	if (is_prefix(**argv, "id")) {
		unsigned int id;
		char *endptr;

		NEXT_ARGP();

		id = strtoul(**argv, &endptr, 0);
		if (*endptr) {
			p_err("can't parse %s as ID", **argv);
			return -1;
		}
		NEXT_ARGP();

		(*fds)[0] = bpf_map_get_fd_by_id(id);
		if ((*fds)[0] < 0) {
			p_err("get map by id (%u): %s", id, strerror(errno));
			return -1;
		}
		return 1;
	} else if (is_prefix(**argv, "name")) {
		char *name;

		NEXT_ARGP();

		name = **argv;
		if (strlen(name) > BPF_OBJ_NAME_LEN - 1) {
			p_err("can't parse name");
			return -1;
		}
		NEXT_ARGP();

		return map_fd_by_name(name, fds);
	} else if (is_prefix(**argv, "pinned")) {
		char *path;

		NEXT_ARGP();

		path = **argv;
		NEXT_ARGP();

		(*fds)[0] = open_obj_pinned_any(path, BPF_OBJ_MAP);
		if ((*fds)[0] < 0)
			return -1;
		return 1;
	}

	p_err("expected 'id', 'name' or 'pinned', got: '%s'?", **argv);
	return -1;
}

int map_parse_fd(int *argc, char ***argv)
{
	int *fds = NULL;
	int nb_fds, fd;

	fds = malloc(sizeof(int));
	if (!fds) {
		p_err("mem alloc failed");
		return -1;
	}
	nb_fds = map_parse_fds(argc, argv, &fds);
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

int map_parse_fd_and_info(int *argc, char ***argv, void *info, __u32 *info_len)
{
	int err;
	int fd;

	fd = map_parse_fd(argc, argv);
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

static int alloc_key_value(struct bpf_map_info *info, void **key, void **value)
{
	*key = NULL;
	*value = NULL;

	if (info->key_size) {
		*key = malloc(info->key_size);
		if (!*key) {
			p_err("key mem alloc failed");
			return -1;
		}
	}

	if (info->value_size) {
		*value = alloc_value(info);
		if (!*value) {
			p_err("value mem alloc failed");
			free(*key);
			*key = NULL;
			return -1;
		}
	}

	return 0;
}

static int parse_elem(char **argv, struct bpf_map_info *info,
		      void *key, void *value, __u32 key_size, __u32 value_size,
		      __u32 *flags, __u32 **value_fd)
{
	if (!*argv) {
		if (!key && !value)
			return 0;
		p_err("did not find %s", key ? "key" : "value");
		return -1;
	}

	if (is_prefix(*argv, "key")) {
		if (!key) {
			if (key_size)
				p_err("duplicate key");
			else
				p_err("unnecessary key");
			return -1;
		}

		argv = parse_bytes(argv + 1, "key", key, key_size);
		if (!argv)
			return -1;

		return parse_elem(argv, info, NULL, value, key_size, value_size,
				  flags, value_fd);
	} else if (is_prefix(*argv, "value")) {
		int fd;

		if (!value) {
			if (value_size)
				p_err("duplicate value");
			else
				p_err("unnecessary value");
			return -1;
		}

		argv++;

		if (map_is_map_of_maps(info->type)) {
			int argc = 2;

			if (value_size != 4) {
				p_err("value smaller than 4B for map in map?");
				return -1;
			}
			if (!argv[0] || !argv[1]) {
				p_err("not enough value arguments for map in map");
				return -1;
			}

			fd = map_parse_fd(&argc, &argv);
			if (fd < 0)
				return -1;

			*value_fd = value;
			**value_fd = fd;
		} else if (map_is_map_of_progs(info->type)) {
			int argc = 2;

			if (value_size != 4) {
				p_err("value smaller than 4B for map of progs?");
				return -1;
			}
			if (!argv[0] || !argv[1]) {
				p_err("not enough value arguments for map of progs");
				return -1;
			}
			if (is_prefix(*argv, "id"))
				p_info("Warning: updating program array via MAP_ID, make sure this map is kept open\n"
				       "         by some process or pinned otherwise update will be lost");

			fd = prog_parse_fd(&argc, &argv);
			if (fd < 0)
				return -1;

			*value_fd = value;
			**value_fd = fd;
		} else {
			argv = parse_bytes(argv, "value", value, value_size);
			if (!argv)
				return -1;

			fill_per_cpu_value(info, value);
		}

		return parse_elem(argv, info, key, NULL, key_size, value_size,
				  flags, NULL);
	} else if (is_prefix(*argv, "any") || is_prefix(*argv, "noexist") ||
		   is_prefix(*argv, "exist")) {
		if (!flags) {
			p_err("flags specified multiple times: %s", *argv);
			return -1;
		}

		if (is_prefix(*argv, "any"))
			*flags = BPF_ANY;
		else if (is_prefix(*argv, "noexist"))
			*flags = BPF_NOEXIST;
		else if (is_prefix(*argv, "exist"))
			*flags = BPF_EXIST;

		return parse_elem(argv + 1, info, key, value, key_size,
				  value_size, NULL, value_fd);
	}

	p_err("expected key or value, got: %s", *argv);
	return -1;
}

static int do_lookup(int argc, char **argv)
{
	struct bpf_map_info info = {};
	__u32 len = sizeof(info);
	void *key, *value;
	int err;
	int fd;

	if (argc < 2)
		usage();

	fd = map_parse_fd_and_info(&argc, &argv, &info, &len);
	if (fd < 0)
		return -1;

	err = alloc_key_value(&info, &key, &value);
	if (err)
		goto exit_free;

	err = parse_elem(argv, &info, key, NULL, info.key_size, 0, NULL, NULL);
	if (err)
		goto exit_free;

	err = bpf_map_lookup_elem(fd, key, value);
	if (err) {
		if (errno == ENOENT) {
			if (json_output) {
				jsonw_null(json_wtr);
			} else {
				printf("key:\n");
				fprint_hex(stdout, key, info.key_size, " ");
				printf("\n\nNot found\n");
			}
		} else {
			p_err("lookup failed: %s", strerror(errno));
		}

		goto exit_free;
	}

	/* here means bpf_map_lookup_elem() succeeded */
	print_key_value(&info, key, value);

exit_free:
	free(key);
	free(value);
	close(fd);

	return err;
}
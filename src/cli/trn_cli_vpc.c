// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_vpc.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief CLI subcommands related to VPC
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
#include "trn_cli.h"

int trn_cli_update_vpc_subcmd(CLIENT *clnt, int argc, char *argv[])
{
	ketopt_t om = KETOPT_INIT;
	struct cli_conf_data_t conf;
	cJSON *json_str = NULL;

	if (trn_cli_read_conf_str(&om, argc, argv, &conf)) {
		return -EINVAL;
	}

	char *buf = conf.conf_str;
	json_str = trn_cli_parse_json(buf);

	if (json_str == NULL) {
		return -EINVAL;
	}

	int *rc;
	struct rpc_trn_vpc_t vpc;
	char rpc[] = "update_vpc_1";

	uint32_t routers[RPC_TRN_MAX_VPC_ROUTERS];
	vpc.routers_ips.routers_ips_val = routers;
	vpc.routers_ips.routers_ips_len = 0;
	vpc.interface = conf.intf;

	int err = trn_cli_parse_vpc(json_str, &vpc);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing VPC config.\n");
		return -EINVAL;
	}

	rc = update_vpc_1(&vpc, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_vpc_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	dump_vpc(&vpc);
	print_msg(
		"update_vpc_1 successfully updated vpc %ld on interface %s.\n",
		vpc.tunid, vpc.interface);
	return 0;
}

int trn_cli_get_vpc_subcmd(CLIENT *clnt, int argc, char *argv[])
{
	ketopt_t om = KETOPT_INIT;
	struct cli_conf_data_t conf;
	cJSON *json_str = NULL;

	if (trn_cli_read_conf_str(&om, argc, argv, &conf)) {
		return -EINVAL;
	}

	char *buf = conf.conf_str;
	json_str = trn_cli_parse_json(buf);

	if (json_str == NULL) {
		return -EINVAL;
	}

	int *rc;
	struct rpc_trn_vpc_key_t vpc_key;
	struct rpc_trn_vpc_t *vpc;
	char rpc[] = "get_vpc_1";
	vpc_key.interface = conf.intf;

	int err = trn_cli_parse_vpc_key(json_str, &vpc_key);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing VPC config.\n");
		return -EINVAL;
	}

	vpc = get_vpc_1(&vpc_key, clnt);
	if (vpc == NULL || strlen(vpc->interface) == 0) {
		print_err("RPC Error: client call failed: get_vpc_1.\n");
		return -EINVAL;
	}

	dump_vpc(vpc);
	print_msg("get_vpc_1 successfully queried vpc %ld on interface %s.\n",
		  vpc->tunid, vpc->interface);

	return 0;
}

void dump_vpc(struct rpc_trn_vpc_t *vpc)
{
	int i;
	print_msg("Interface: %s\n", vpc->interface);
	print_msg("Tunnel ID: %ld\n", vpc->tunid);
	print_msg("Routers IPs: [");
	for (i = 0; i < vpc->routers_ips.routers_ips_len; i++) {
		print_msg("0x%x", ntohl(vpc->routers_ips.routers_ips_val[i]));
		if (i < vpc->routers_ips.routers_ips_len - 1)
			print_msg(", ");
	}
	print_msg("]\n");
}
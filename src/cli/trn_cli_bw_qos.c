// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_bw_qos.c
 * @author Vinay Kulkarni		(@vinaykul)
 *
 * @brief Transit Agent cli subcommands related to Bandwidth QoS configuration
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
#include "trn_cli.h"

int trn_cli_update_bw_qos_config_subcmd(CLIENT *clnt, int argc, char *argv[])
{
	ketopt_t om = KETOPT_INIT;
	cJSON *json_str = NULL;
	struct cli_conf_data_t conf;

	if (trn_cli_read_conf_str(&om, argc, argv, &conf)) {
		return -EINVAL;
	}

	char *buf = conf.conf_str;
	json_str = trn_cli_parse_json(buf);
	if (json_str == NULL) {
		return -EINVAL;
	}

	int *rc;
	rpc_trn_bw_qos_config_t bw_qos_config;
	char rpc[] = "update_bw_qos_config_1";
	bw_qos_config.interface = conf.intf;

	int err = trn_cli_parse_bw_qos_config(json_str, &bw_qos_config);
	cJSON_Delete(json_str);
	json_str = NULL;
	if (err != 0) {
		print_err("Error: parsing bandwidth qos config.\n");
		return -EINVAL;
	}

	rc = update_bw_qos_config_1(&bw_qos_config, clnt);
	if (rc == (int *)NULL) {
		print_err("Error: call failed: update_bw_qos_config_1.\n");
		return -EINVAL;
	}
	if (*rc != 0) {
		print_err("Error: %s fatal error, see transitd logs for details.\n",
				rpc);
		return -EINVAL;
	}

	print_msg("update_bw_qos_config_1 successfully updated egress bw limit %lu bytes/sec on interface %s saddr 0x%x.\n",
			bw_qos_config.egress_bandwidth_bytes_per_sec, bw_qos_config.interface, bw_qos_config.saddr);
	return 0;
}

int trn_cli_delete_bw_qos_config_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	rpc_trn_bw_qos_config_key_t key;
	char rpc[] = "delete_bw_qos_config_1";
	key.interface = conf.intf;

	int err = trn_cli_parse_bw_qos_config_key(json_str, &key);
	cJSON_Delete(json_str);
	if (err != 0) {
		print_err("Error: parsing bw qos config key.\n");
		return -EINVAL;
	}

	rc = delete_bw_qos_config_1(&key, clnt);
	if (rc == (int *)NULL) {
		print_err("Error: call failed: delete_bw_qos_config_1.\n");
		return -EINVAL;
	}
	if (*rc != 0) {
		print_err("Error: %s fatal error, see transitd logs for details.\n",
				rpc);
		return -EINVAL;
	}

	print_msg("delete_bw_qos_config_1 successfully deleted bw qos config on interface %s.\n",
			key.interface);
	return 0;
}

int trn_cli_get_bw_qos_config_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_bw_qos_config_key_t bwqoskey;
	struct rpc_trn_bw_qos_config_t *bwqoscfg;
	char rpc[] = "get_bw_qos_config_1";
	bwqoskey.interface = conf.intf;

	int err = trn_cli_parse_bw_qos_config_key(json_str, &bwqoskey);
	cJSON_Delete(json_str);
	if (err != 0) {
		print_err("Error: parsing bw qos config key.\n");
		return -EINVAL;
	}

	bwqoscfg = get_bw_qos_config_1(&bwqoskey, clnt);
	if (bwqoscfg == NULL || strlen(bwqoscfg->interface) == 0) {
		print_err("RPC Error: client call failed: get_bw_qos_config_1.\n");
		return -EINVAL;
	}

	dump_bw_qos_config(bwqoscfg);
	print_msg("getbw_qos_config_1 successfully queried for saddr 0x%x, interface %s.\n",
			bwqoscfg->saddr, bwqoscfg->interface);
	return 0;
}

void dump_bw_qos_config(struct rpc_trn_bw_qos_config_t *bw_qos_config)
{
	print_msg("Interface: %s\n", bw_qos_config->interface);
	print_msg("Source Address: 0x%x\n", bw_qos_config->saddr);
	print_msg("Egress Bandwidth: %lu bytes/sec\n", bw_qos_config->egress_bandwidth_bytes_per_sec);
}

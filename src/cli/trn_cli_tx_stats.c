// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_tx_stats.c
 * @author Vinay Kulkarni		(@vinaykul)
 *
 * @brief Transit Agent cli subcommands for Tx stats
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

int trn_cli_update_tx_stats_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	rpc_trn_tx_stats_t tx_stats;
	char rpc[] = "update_tx_stats_1";
	tx_stats.interface = conf.intf;

	int err = trn_cli_parse_tx_stats(json_str, &tx_stats);
	cJSON_Delete(json_str);
	json_str = NULL;
	if (err != 0) {
		print_err("Error: parsing tx_stats config.\n");
		return -EINVAL;
	}

	rc = update_tx_stats_1(&tx_stats, clnt);
	if (rc == (int *)NULL) {
		print_err("Error: call failed: update_tx_stats_1.\n");
		return -EINVAL;
	}
	if (*rc != 0) {
		print_err("Error: %s fatal error, see transitd logs for details.\n",
				rpc);
		return -EINVAL;
	}

	print_msg("update_tx_stats_1 successfully updated stats on interface %s saddr 0x%x.\n",
			tx_stats.interface, tx_stats.saddr);
	return 0;
}

int trn_cli_get_tx_stats_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_tx_stats_key_t tx_stats_key;
	struct rpc_trn_tx_stats_t *tx_stats;
	char rpc[] = "get_tx_stats_1";
	tx_stats_key.interface = conf.intf;

	int err = trn_cli_parse_tx_stats_key(json_str, &tx_stats_key);
	cJSON_Delete(json_str);
	if (err != 0) {
		print_err("Error: parsing tx_stats_key.\n");
		return -EINVAL;
	}

	tx_stats = get_tx_stats_1(&tx_stats_key, clnt);
	if (tx_stats == NULL || strlen(tx_stats->interface) == 0) {
		print_err("RPC Error: client call failed: get_tx_stats_1.\n");
		return -EINVAL;
	}

	dump_tx_stats(tx_stats);
	print_msg("get_tx_stats_1 successfully queried tx stats for saddr 0x%x, interface %s.\n",
			tx_stats->saddr, tx_stats->interface);
	return 0;
}

void dump_tx_stats(struct rpc_trn_tx_stats_t *tx_stats)
{
	print_msg("Interface:             %s\n", tx_stats->interface);
	print_msg("Source Address:        0x%x\n", tx_stats->saddr);
	print_msg("tx_pkts_xdp_redirect:  %u\n", tx_stats->tx_pkts_xdp_redirect);
	print_msg("tx_bytes_xdp_redirect: %lu\n", tx_stats->tx_bytes_xdp_redirect);
	print_msg("tx_pkts_xdp_pass:      %u\n", tx_stats->tx_pkts_xdp_pass);
	print_msg("tx_bytes_xdp_pass:     %lu\n", tx_stats->tx_bytes_xdp_pass);
	print_msg("tx_pkts_xdp_drop:      %u\n", tx_stats->tx_pkts_xdp_drop);
	print_msg("tx_bytes_xdp_drop:     %lu\n", tx_stats->tx_bytes_xdp_drop);
}

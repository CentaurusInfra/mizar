// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_net.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief CLI subcommands related to networks
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

int trn_cli_update_net_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	rpc_trn_network_t net;
	char rpc[] = "update_net_1";

	uint32_t switches[RPC_TRN_MAX_NET_SWITCHES];
	net.switches_ips.switches_ips_val = switches;
	net.switches_ips.switches_ips_len = 0;
	net.interface = conf.intf;

	int err = trn_cli_parse_net(json_str, &net);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network config.\n");
		return -EINVAL;
	}

	rc = update_net_1(&net, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_net_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	dump_net(&net);
	print_msg(
		"update_net_1 successfully updated network %d on interface %s\n",
		net.netip, net.interface);
	return 0;
}

int trn_cli_get_net_subcmd(CLIENT *clnt, int argc, char *argv[])
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

	rpc_trn_network_key_t net_key;
	rpc_trn_network_t *net;
	char rpc[] = "get_net_1";
	net_key.interface = conf.intf;

	int err = trn_cli_parse_net_key(json_str, &net_key);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network config.\n");
		return -EINVAL;
	}

	net = get_net_1(&net_key, clnt);
	if (net == NULL || strlen(net->interface) == 0) {
		print_err("RPC Error: client call failed: get_net_1.\n");
		return -EINVAL;
	}

	dump_net(net);
	print_msg(
		"get_net_1 successfully queried network %d with prefix length %d on interface %s, with tunneld id %ld.\n",
		net->netip, net->prefixlen, net->interface, net->tunid);

	return 0;
}

void dump_net(struct rpc_trn_network_t *net)
{
	int i;
	print_msg("Interface: %s\n", net->interface);
	print_msg("Tunnel ID: %ld\n", net->tunid);
	print_msg("Network Address: 0x%x/%d\n", net->netip, net->prefixlen);
	print_msg("Switches IPs: [");
	for (i = 0; i < net->switches_ips.switches_ips_len; i++) {
		print_msg("0x%x", ntohl(net->switches_ips.switches_ips_val[i]));
		if (i < net->switches_ips.switches_ips_len - 1)
			print_msg(", ");
	}
	print_msg("]\n");
}
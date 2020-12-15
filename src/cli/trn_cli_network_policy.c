// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_net.c
 * @author Catherine Lu (@clu2)
 *         
 * @brief CLI subcommands related to networks
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

#include "trn_cli.h"

int trn_cli_update_transit_network_policy_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_cidr_t cidrval;
	char rpc[] = "update_transit_network_policy_1";
	cidrval.interface = conf.intf;

	int err = trn_cli_parse_network_policy_cidr(json_str, &cidrval);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy config.\n");
		return -EINVAL;
	}

	rc = update_transit_network_policy_1(&cidrval, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_transit_network_policy_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	dump_network_policy(&cidrval);
	print_msg("update_transit_network_policy_1 successfully updated network policy\n");
	
	return 0;
}

int trn_cli_delete_transit_network_policy_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_cidr_key_t cidrkey;
	char rpc[] = "delete_transit_network_policy_1";
	cidrkey.interface = conf.intf;

	int err = trn_cli_parse_network_policy_cidr_key(json_str, &cidrkey);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy config.\n");
		return -EINVAL;
	}

	rc = delete_transit_network_policy_1(&cidrkey, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: delete_transit_network_policy_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("delete_transit_network_policy_1 successfully deleted network policy cidr: 0x%x / %d, for interface %s\n",
				cidrkey.cidr_ip, cidrkey.cidr_prefixlen, cidrkey.interface);

	return 0;
}

int trn_cli_update_transit_network_policy_enforcement_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_enforce_t enforce;
	char rpc[] = "update_transit_network_policy_enforcement_1";
	enforce.interface = conf.intf;

	int err = trn_cli_parse_network_policy_enforcement(json_str, &enforce);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy enforcement config.\n");
		return -EINVAL;
	}

	rc = update_transit_network_policy_enforcement_1(&enforce, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_transit_network_policy_enforcement_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	dump_enforced_policy(&enforce);
	print_msg("update_transit_network_policy_enforcement_1 successfully updated network policy\n");

	return 0;
}

void dump_network_policy(struct rpc_trn_vsip_cidr_t *policy)
{
	print_msg("Interface: %s\n", policy->interface);
	print_msg("Tunnel ID: %ld\n", policy->tunid);
	print_msg("Local IP: %x\n", policy->local_ip);
	print_msg("CIDR Prefix: %d\n", policy->cidr_prefixlen);
	print_msg("CIDR IP: %x\n", policy->cidr_ip);
	print_msg("CIDR Type: %d\n", policy->cidr_type);
	print_msg("bit value: %ld\n", policy->bit_val);
}

void dump_enforced_policy(struct rpc_trn_vsip_enforce_t *enforce)
{
	print_msg("Interface: %s\n", enforce->interface);
	print_msg("Tunnel ID: %ld\n", enforce->tunid);
	print_msg("Local IP: %x\n", enforce->local_ip);
}

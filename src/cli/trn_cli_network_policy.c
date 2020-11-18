// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_network_policy.c
 * @author Cathy Lu (@clu2)
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

int trn_cli_update_network_policy_ingress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ip_cidr_t cidrval;
	char rpc[] = "update_network_policy_ingress_1";

	int err = trn_cli_parse_network_policy_cidr(json_str, &cidrval);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy config.\n");
		return -EINVAL;
	}
 
	rc = update_network_policy_ingress_1(&cidrval, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_network_policy_ingress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("update_network_policy_ingress_1 successfully updated network policy\n");
	
	return 0;
}

int trn_cli_update_network_policy_egress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ip_cidr_t cidrval;
	char rpc[] = "update_network_policy_egress_1";

	int err = trn_cli_parse_network_policy_cidr(json_str, &cidrval);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy config.\n");
		return -EINVAL;
	}
 
	rc = update_network_policy_egress_1(&cidrval, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_network_policy_egress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("update_network_policy_egress_1 successfully updated network policy\n");
	
	return 0;
}

int trn_cli_delete_network_policy_ingress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ip_cidr_key_t cidrkey;
	char rpc[] ="delete_network_policy_ingress_1";

	int err = trn_cli_parse_network_policy_cidr_key(json_str, &cidrkey);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy config.\n");
		return -EINVAL;
	}
 
	rc = delete_network_policy_ingress_1(&cidrkey, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: delete_network_policy_ingress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("delete_network_policy_ingress_1 successfully deleted network policy\n");
	
	return 0;
}

int trn_cli_delete_network_policy_egress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ip_cidr_key_t cidrkey;
	char rpc[] ="delete_network_policy_egress_1";

	int err = trn_cli_parse_network_policy_cidr_key(json_str, &cidrkey);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy config.\n");
		return -EINVAL;
	}
 
	rc = delete_network_policy_egress_1(&cidrkey, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: delete_network_policy_egress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("delete_network_policy_egress_1 successfully deleted network policy\n");
	
	return 0;
}

int trn_cli_update_network_policy_protocol_port_ingress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ppo_t ppo;
	char rpc[] = "update_network_policy_protocol_port_ingress_1";

	int err = trn_cli_parse_network_policy_ppo(json_str, &ppo);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy protocol port config.\n");
		return -EINVAL;
	}
 
	rc = update_network_policy_protocol_port_ingress_1(&ppo, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_network_policy_protocol_port_ingress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("update_network_policy_protocol_port_ingress_1 successfully updated network policy\n");
	
	return 0;
}

int trn_cli_update_network_policy_protocol_port_egress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ppo_t ppo;
	char rpc[] = "update_network_policy_protocol_port_egress_1";

	int err = trn_cli_parse_network_policy_ppo(json_str, &ppo);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy protocol port config.\n");
		return -EINVAL;
	}
 
	rc = update_network_policy_protocol_port_egress_1(&ppo, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_network_policy_protocol_port_egress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("update_network_policy_protocol_port_egress_1 successfully updated network policy\n");
	
	return 0;
}

int trn_cli_delete_network_policy_protocol_port_ingress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ppo_key_t ppokey;
	char rpc[] = "delete_network_policy_protocol_port_ingress_1";

	int err = trn_cli_parse_network_policy_ppo_key(json_str, &ppokey);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy protocol port config.\n");
		return -EINVAL;
	}
 
	rc = delete_network_policy_protocol_port_ingress_1(&ppokey, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: delete_network_policy_protocol_port_ingress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("delete_network_policy_protocol_port_ingress_1 successfully deleted network policy\n");
	
	return 0;
}

int trn_cli_delete_network_policy_protocol_port_egress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_vsip_ppo_key_t ppokey;
	char rpc[] = "delete_network_policy_protocol_port_egress_1";

	int err = trn_cli_parse_network_policy_ppo_key(json_str, &ppokey);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy protocol port config.\n");
		return -EINVAL;
	}
 
	rc = delete_network_policy_protocol_port_egress_1(&ppokey, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: delete_network_policy_protocol_port_egress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("delete_network_policy_protocol_port_egress_1 successfully deleted network policy\n");
	
	return 0;
}

int trn_cli_update_network_policy_enforcement_map_ingress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_enforced_ip_t enforcement;
	char rpc[] = "update_network_policy_enforcement_map_ingress_1";

	int err = trn_cli_parse_network_policy_enforce(json_str, &enforcement);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy enforcement map config.\n");
		return -EINVAL;
	}
 
	rc = update_network_policy_enforcement_map_ingress_1(&enforcement, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_network_policy_enforcement_map_ingress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("update_network_policy_enforcement_map_ingress_1 successfully updated network policy\n");
	
	return 0;
}

int trn_cli_update_network_policy_enforcement_map_egress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_enforced_ip_t enforcement;
	char rpc[] = "update_network_policy_enforcement_map_egress_1";

	int err = trn_cli_parse_network_policy_enforce(json_str, &enforcement);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy enforcement map config.\n");
		return -EINVAL;
	}
 
	rc = update_network_policy_enforcement_map_egress_1(&enforcement, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: update_network_policy_enforcement_map_egress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("update_network_policy_enforcement_map_egress_1 successfully updated network policy\n");
	
	return 0;
}

int trn_cli_delete_network_policy_enforcement_map_ingress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_enforced_ip_t enforcement;
	char rpc[] = "delete_network_policy_enforcement_map_ingress_1";

	int err = trn_cli_parse_network_policy_enforce(json_str, &enforcement);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy enforcement map config.\n");
		return -EINVAL;
	}
 
	rc = delete_network_policy_enforcement_map_ingress_1(&enforcement, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: delete_network_policy_enforcement_map_ingress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("delete_network_policy_enforcement_map_ingress_1 successfully deleted network policy\n");
	
	return 0;
}

int trn_cli_delete_network_policy_enforcement_map_egress_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	struct rpc_trn_enforced_ip_t enforcement;
	char rpc[] = "delete_network_policy_enforcement_map_egress_1";

	int err = trn_cli_parse_network_policy_enforce(json_str, &enforcement);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing network policy enforcement map config.\n");
		return -EINVAL;
	}
 
	rc = delete_network_policy_enforcement_map_egress_1(&enforcement, clnt);
	if (rc == (int *)NULL) {
		print_err("RPC Error: client call failed: delete_network_policy_enforcement_map_egress_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal daemon error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg("delete_network_policy_enforcement_map_egress_1 successfully deleted network policy\n");
	
	return 0;
}

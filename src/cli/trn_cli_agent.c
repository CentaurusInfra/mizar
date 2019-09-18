// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_agent.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief Transit Agent cli subcommands
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

int trn_cli_update_agent_ep_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	rpc_trn_endpoint_t ep;
	char rpc[] = "update_agent_ep_1";

	char veth[20];
	char hosted_itf[20];
	uint32_t remote_ips[RPC_TRN_MAX_REMOTE_IPS];
	ep.remote_ips.remote_ips_val = remote_ips;
	ep.remote_ips.remote_ips_len = 0;
	ep.veth = veth;
	ep.hosted_interface = hosted_itf;
	ep.interface = conf.intf;

	int err = trn_cli_parse_ep(json_str, &ep);
	cJSON_Delete(json_str);
	json_str = NULL;

	if (err != 0) {
		print_err("Error: parsing endpoint config.\n");
		return -EINVAL;
	}

	rc = update_agent_ep_1(&ep, clnt);
	if (rc == (int *)NULL) {
		print_err("Error: call failed: update_agent_ep_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_err(
			"Error: %s fatal error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	print_msg(
		"update_agent_ep_1 successfully updated endpoint %d on interface %s.\n",
		ep.ip, ep.interface);
	return 0;
}

int trn_cli_get_agent_ep_subcmd(CLIENT *clnt, int argc, char *argv[])
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

	rpc_trn_endpoint_key_t epkey;
	rpc_trn_endpoint_t *ep;
	char rpc[] = "get_agent_ep_1";
	epkey.interface = conf.intf;

	int err = trn_cli_parse_ep_key(json_str, &epkey);
	cJSON_Delete(json_str);

	if (err != 0) {
		print_err("Error: parsing endpoint config.\n");
		return -EINVAL;
	}

	ep = get_agent_ep_1(&epkey, clnt);
	if (ep == NULL || strlen(ep->interface) == 0) {
		print_err("RPC Error: client call failed: get_agent_ep_1.\n");
		return -EINVAL;
	}

	dump_ep(ep);
	print_msg(
		"get_agent_ep_1 successfully queried endpoint %d on interface %s.\n",
		ep->ip, ep->interface);

	return 0;
}

int trn_cli_update_agent_md_subcmd(CLIENT *clnt, int argc, char *argv[])
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
	rpc_trn_agent_metadata_t agent_md;
	char rpc[] = "update_agent_md_1";

	agent_md.interface = conf.intf;

	char veth[20];
	char hosted_itf[20];
	uint32_t remote_ips[RPC_TRN_MAX_REMOTE_IPS];
	agent_md.ep.remote_ips.remote_ips_val = remote_ips;
	agent_md.ep.remote_ips.remote_ips_len = 0;
	agent_md.ep.veth = veth;
	agent_md.ep.hosted_interface = hosted_itf;
	agent_md.ep.interface = conf.intf; // Unused

	uint32_t switches[RPC_TRN_MAX_NET_SWITCHES];
	agent_md.net.switches_ips.switches_ips_val = switches;
	agent_md.net.switches_ips.switches_ips_len = 0;
	agent_md.net.interface = conf.intf; // Unused

	char eth_itf[20];
	agent_md.eth.interface = eth_itf;
	int err = trn_cli_parse_agent_md(json_str, &agent_md);
	cJSON_Delete(json_str);

	if (err) {
		print_err("Error: parsing agent metadata config.\n");
		return -EINVAL;
	}

	rc = update_agent_md_1(&agent_md, clnt);
	if (rc == (int *)NULL) {
		print_err("Error: call failed: update_agent_md_1.\n");
		return -EINVAL;
	}

	if (*rc != 0) {
		print_msg(
			"Error: %s fatal error, see transitd logs for details.\n",
			rpc);
		return -EINVAL;
	}

	dump_agent_md(&agent_md);
	print_msg(
		"update_agent_md_1 successfully updated ep metadata on interface %s.\n",
		agent_md.interface);

	return 0;
}

int trn_cli_get_agent_md_subcmd(CLIENT *clnt, int argc, char *argv[])
{
	ketopt_t om = KETOPT_INIT;
	struct cli_conf_data_t conf;

	if (trn_cli_read_conf_str(&om, argc, argv, &conf)) {
		return -EINVAL;
	}

	rpc_trn_agent_metadata_t *agent_md;
	rpc_intf_t itf;
	itf.interface = conf.intf;

	char rpc[] = "get_agent_md_1";
	agent_md = get_agent_md_1(&itf, clnt);
	if (agent_md == NULL || strlen(agent_md->interface) == 0) {
		print_err("Error: call failed: get_agent_md_1.\n");
		return -EINVAL;
	}

	dump_agent_md(agent_md);
	print_msg(
		"get_agent_md_1 successfully queried ep metadata on interface %s.\n",
		agent_md->interface);
	return 0;
}

void dump_agent_md(struct rpc_trn_agent_metadata_t *agent_md)
{
	int i;
	print_msg("Endpoint Interface: %s\n", agent_md->ep.interface);
	print_msg("Endpoint Tunnel ID: %ld\n", agent_md->ep.tunid);
	print_msg("Endpoint IP: 0x%x\n", agent_md->ep.ip);
	print_msg("Endpoint Hosted Interface: %s\n",
		  agent_md->ep.hosted_interface);
	print_msg("Endpoint veth: %s\n", agent_md->ep.veth);
	print_msg("Endpoint EP Type: %d\n", agent_md->ep.eptype);
	print_msg("Endpoint Remote IPs: [");
	for (i = 0; i < agent_md->ep.remote_ips.remote_ips_len; i++) {
		print_msg("0x%x",
			  ntohl(agent_md->ep.remote_ips.remote_ips_val[i]));
		if (i < agent_md->ep.remote_ips.remote_ips_len - 1)
			print_msg(", ");
	}
	print_msg("]\n");

	print_msg("Network Interface: %s\n", agent_md->net.interface);
	print_msg("Network Tunnel ID: %ld\n", agent_md->net.tunid);
	print_msg("Network Address: 0x%x/%d\n", agent_md->net.netip,
		  agent_md->net.prefixlen);
	print_msg("Switches IPs: [");
	for (i = 0; i < agent_md->net.switches_ips.switches_ips_len; i++) {
		print_msg(
			"0x%x",
			ntohl(agent_md->net.switches_ips.switches_ips_val[i]));
		if (i < agent_md->net.switches_ips.switches_ips_len - 1)
			print_msg(", ");
	}
	print_msg("]\n");

	print_msg("eth: %s, 0x%x\n", agent_md->eth.interface, agent_md->eth.ip);
}

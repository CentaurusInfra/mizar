// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file trn_cli_common.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief Defines common functions for parsing CLI input
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

cJSON *trn_cli_parse_json(const char *buf)
{
	cJSON *conf_json = cJSON_Parse(buf);
	if (conf_json == NULL) {
		const char *error_ptr = cJSON_GetErrorPtr();
		if (error_ptr != NULL) {
			print_err("Error: parsing json string before: %s.\n",
				  error_ptr);
		}
		return NULL;
	}
	return conf_json;
}

int trn_cli_parse_vpc(const cJSON *jsonobj, rpc_trn_vpc_t *vpc)
{
	cJSON *tunnel_id = cJSON_GetObjectItem(jsonobj, "tunnel_id");
	cJSON *routers_ips = cJSON_GetObjectItem(jsonobj, "routers_ips");
	cJSON *router_ip = NULL;
	int retval = 0;

	if (tunnel_id == NULL) {
		vpc->tunid = 0;
	} else if (cJSON_IsString(tunnel_id)) {
		vpc->tunid = atoi(tunnel_id->valuestring);
	} else {
		print_err("Error: vpc tunnel_id is non-string.\n");
		return -EINVAL;
	}

	int i = 0;
	vpc->routers_ips.routers_ips_len = 0;
	cJSON_ArrayForEach(router_ip, routers_ips)
	{
		if (cJSON_IsString(router_ip)) {
			struct sockaddr_in sa;
			inet_pton(AF_INET, router_ip->valuestring,
				  &(sa.sin_addr));
			vpc->routers_ips.routers_ips_val[i] =
				sa.sin_addr.s_addr;
			vpc->routers_ips.routers_ips_len++;
		} else {
			print_err("Error: vpc router ip is non-string.\n");
			return -EINVAL;
		}
		i++;
		if (i == RPC_TRN_MAX_REMOTE_IPS) {
			print_err(
				"Warning: router ip addresses reached max limited, continuing with sublist.\n");
			retval = -EMSGSIZE;
			break;
		}
	}
	return retval;
}

int trn_cli_parse_vpc_key(const cJSON *jsonobj, rpc_trn_vpc_key_t *vpc)
{
	cJSON *tunnel_id = cJSON_GetObjectItem(jsonobj, "tunnel_id");
	cJSON *routers_ips = cJSON_GetObjectItem(jsonobj, "routers_ips");
	cJSON *router_ip = NULL;
	int retval = 0;

	if (tunnel_id == NULL) {
		vpc->tunid = 0;
	} else if (cJSON_IsString(tunnel_id)) {
		vpc->tunid = atoi(tunnel_id->valuestring);
	} else {
		print_err("Error: vpc tunnel_id is non-string.\n");
		return -EINVAL;
	}
	return retval;
}

int trn_cli_parse_net(const cJSON *jsonobj, struct rpc_trn_network_t *net)
{
	cJSON *tunnel_id = cJSON_GetObjectItem(jsonobj, "tunnel_id");
	cJSON *nip = cJSON_GetObjectItem(jsonobj, "nip");
	cJSON *prefixlen = cJSON_GetObjectItem(jsonobj, "prefixlen");
	cJSON *switches_ips = cJSON_GetObjectItem(jsonobj, "switches_ips");
	cJSON *switch_ip = NULL;

	if (cJSON_IsString(tunnel_id)) {
		uint64_t tid = atoi(tunnel_id->valuestring);
		net->tunid = tid;
	} else {
		print_err("Error: Net Tunnel ID Error\n");
		return -EINVAL;
	}

	if (nip != NULL && cJSON_IsString(nip)) {
		struct sockaddr_in sa;
		inet_pton(AF_INET, nip->valuestring, &(sa.sin_addr));
		net->netip = sa.sin_addr.s_addr;
	} else {
		print_err("Error: Net IP is missing or non-string\n");
		return -EINVAL;
	}

	if (cJSON_IsString(prefixlen)) {
		net->prefixlen = atoi(prefixlen->valuestring);
	} else {
		print_err("Error: Net prefixlen Error\n");
		return -EINVAL;
	}

	int i = 0;
	net->switches_ips.switches_ips_len = 0;
	cJSON_ArrayForEach(switch_ip, switches_ips)
	{
		if (cJSON_IsString(switch_ip)) {
			struct sockaddr_in sa;
			inet_pton(AF_INET, switch_ip->valuestring,
				  &(sa.sin_addr));
			net->switches_ips.switches_ips_val[i] =
				sa.sin_addr.s_addr;
			i++;
		} else {
			print_err("Error: Net Switch IP is non-string\n");
			return -EINVAL;
		}
		if (i == RPC_TRN_MAX_NET_SWITCHES) {
			print_err("(Warning) Switch IPS reached max limited\n");
			break;
		}
	}
	net->switches_ips.switches_ips_len = i;
	return 0;
}

int trn_cli_parse_net_key(const cJSON *jsonobj,
			  struct rpc_trn_network_key_t *net)
{
	cJSON *tunnel_id = cJSON_GetObjectItem(jsonobj, "tunnel_id");
	cJSON *nip = cJSON_GetObjectItem(jsonobj, "nip");
	cJSON *prefixlen = cJSON_GetObjectItem(jsonobj, "prefixlen");
	cJSON *switches_ips = cJSON_GetObjectItem(jsonobj, "switches_ips");
	cJSON *switch_ip = NULL;

	if (cJSON_IsString(tunnel_id)) {
		uint64_t tid = atoi(tunnel_id->valuestring);
		net->tunid = tid;
	} else {
		print_err("Error: Net Tunnel ID Error\n");
		return -EINVAL;
	}

	if (nip != NULL && cJSON_IsString(nip)) {
		struct sockaddr_in sa;
		inet_pton(AF_INET, nip->valuestring, &(sa.sin_addr));
		net->netip = sa.sin_addr.s_addr;
	} else {
		print_err("Error: Net IP is missing or non-string\n");
		return -EINVAL;
	}

	if (cJSON_IsString(prefixlen)) {
		net->prefixlen = atoi(prefixlen->valuestring);
	} else {
		print_err("Error: Net prefixlen Error\n");
		return -EINVAL;
	}
	return 0;
}

int trn_cli_parse_xdp(const cJSON *jsonobj, rpc_trn_xdp_intf_t *xdp_intf)
{
	cJSON *xdp_path = cJSON_GetObjectItem(jsonobj, "xdp_path");
	cJSON *pcapfile = cJSON_GetObjectItem(jsonobj, "pcapfile");

	if (xdp_path == NULL) {
		print_err("Missing path for xdp program to load.\n");
		return -EINVAL;
	} else if (cJSON_IsString(xdp_path)) {
		strcpy(xdp_intf->xdp_path, xdp_path->valuestring);
	}

	if (pcapfile == NULL) {
		xdp_intf->pcapfile = NULL;
		print_err(
			"Warning: Missing pcapfile. Packet capture will not be available for the interface.\n");
	} else if (cJSON_IsString(pcapfile)) {
		strcpy(xdp_intf->pcapfile, pcapfile->valuestring);
	}
	return 0;
}

int trn_cli_parse_ep(const cJSON *jsonobj, struct rpc_trn_endpoint_t *ep)
{
	cJSON *tunnel_id = cJSON_GetObjectItem(jsonobj, "tunnel_id");
	cJSON *ip = cJSON_GetObjectItem(jsonobj, "ip");
	cJSON *eptype = cJSON_GetObjectItem(jsonobj, "eptype");
	cJSON *mac = cJSON_GetObjectItem(jsonobj, "mac");
	cJSON *veth = cJSON_GetObjectItem(jsonobj, "veth");
	cJSON *remote_ips = cJSON_GetObjectItem(jsonobj, "remote_ips");
	cJSON *remote_ip = NULL;
	cJSON *hosted_iface = cJSON_GetObjectItem(jsonobj, "hosted_iface");

	if (veth == NULL) {
		ep->veth = NULL;
		print_err("Warning: missing veth.\n");
	} else if (cJSON_IsString(
			   veth)) { // This transit is hosting the endpoint
		strcpy(ep->veth, veth->valuestring);
	}

	if (hosted_iface == NULL) {
		ep->hosted_interface = NULL;
		print_err(
			"Warning: missing hosted interface, using default.\n");
	} else if (cJSON_IsString(
			   hosted_iface)) { // This transit is hosting the endpoint
		strcpy(ep->hosted_interface, hosted_iface->valuestring);
	}

	if (tunnel_id == NULL) {
		ep->tunid = 0;
		print_err("Warning: Tunnel ID default is used: %ld\n",
			  ep->tunid);
	} else if (cJSON_IsString(tunnel_id)) {
		ep->tunid = atoi(tunnel_id->valuestring);
	} else {
		print_err("Error: Tunnel ID Error\n");
		return -EINVAL;
	}

	if (ip != NULL && cJSON_IsString(ip)) {
		struct sockaddr_in sa;
		inet_pton(AF_INET, ip->valuestring, &(sa.sin_addr));
		ep->ip = sa.sin_addr.s_addr;
	} else {
		print_err("Error: IP is missing or non-string\n");
		return -EINVAL;
	}

	if (eptype == NULL) {
		ep->eptype = 0;
		print_err("Warning: EP TYpe (default): %d\n", ep->eptype);
	} else if (cJSON_IsString(eptype)) {
		ep->eptype = atoi(eptype->valuestring);
	} else {
		print_err("Error: eptype ID Error\n");
		return -EINVAL;
	}

	if (mac != NULL && cJSON_IsString(mac)) {
		if (6 == sscanf(mac->valuestring,
				"%hhx:%hhx:%hhx:%hhx:%hhx:%hhx%*c", &ep->mac[0],
				&ep->mac[1], &ep->mac[2], &ep->mac[3],
				&ep->mac[4], &ep->mac[5])) {
		} else {
			/* invalid mac */
			print_err("Error: Invalid MAC\n");
			return -EINVAL;
		}
	} else {
		print_err("MAC is missing or non-string\n");
		return -EINVAL;
	}

	int i = 0;
	ep->remote_ips.remote_ips_len = 0;
	cJSON_ArrayForEach(remote_ip, remote_ips)
	{
		if (cJSON_IsString(remote_ip)) {
			struct sockaddr_in sa;
			inet_pton(AF_INET, remote_ip->valuestring,
				  &(sa.sin_addr));
			ep->remote_ips.remote_ips_val[i] = sa.sin_addr.s_addr;
			ep->remote_ips.remote_ips_len++;
		} else {
			print_err("Error: Remote IP is non-string\n");
			return -EINVAL;
		}
		i++;
		if (i == RPC_TRN_MAX_REMOTE_IPS) {
			print_err("Warning: Remote IPS reached max limited\n");
			break;
		}
	}
	return 0;
}

int trn_cli_parse_ep_key(const cJSON *jsonobj,
			 struct rpc_trn_endpoint_key_t *ep)
{
	cJSON *tunnel_id = cJSON_GetObjectItem(jsonobj, "tunnel_id");
	cJSON *ip = cJSON_GetObjectItem(jsonobj, "ip");

	if (tunnel_id == NULL) {
		ep->tunid = 0;
		print_err("Warning: Tunnel ID default is used: %ld\n",
			  ep->tunid);
	} else if (cJSON_IsString(tunnel_id)) {
		ep->tunid = atoi(tunnel_id->valuestring);
	} else {
		print_err("Error: Tunnel ID Error\n");
		return -EINVAL;
	}

	if (ip != NULL && cJSON_IsString(ip)) {
		struct sockaddr_in sa;
		inet_pton(AF_INET, ip->valuestring, &(sa.sin_addr));
		ep->ip = sa.sin_addr.s_addr;
	} else {
		print_err("Error: IP is missing or non-string\n");
		return -EINVAL;
	}

	return 0;
}

int trn_cli_parse_tun_intf(const cJSON *jsonobj, rpc_trn_tun_intf_t *itf)
{
	cJSON *ip = cJSON_GetObjectItem(jsonobj, "ip");
	cJSON *mac = cJSON_GetObjectItem(jsonobj, "mac");
	cJSON *iface = cJSON_GetObjectItem(jsonobj, "iface");

	if (iface == NULL) {
		itf->interface = NULL;
		print_err("Error: Missing hosted interface, using default.\n");
		return -EINVAL;
	} else if (cJSON_IsString(iface)) {
		strcpy(itf->interface, iface->valuestring);
	}

	if (mac != NULL && cJSON_IsString(mac)) {
		if (6 == sscanf(mac->valuestring,
				"%hhx:%hhx:%hhx:%hhx:%hhx:%hhx%*c",
				&itf->mac[0], &itf->mac[1], &itf->mac[2],
				&itf->mac[3], &itf->mac[4], &itf->mac[5])) {
		} else {
			/* invalid mac */
			print_err("Error: Invalid MAC\n");
			return -EINVAL;
		}
	} else {
		print_err("Error: MAC is missing or non-string\n");
		return -EINVAL;
	}

	if (ip != NULL && cJSON_IsString(ip)) {
		struct sockaddr_in sa;
		inet_pton(AF_INET, ip->valuestring, &(sa.sin_addr));
		itf->ip = sa.sin_addr.s_addr;
	} else {
		print_err("Error: IP is missing or non-string\n");
		return -EINVAL;
	}
	return 0;
}

int trn_cli_parse_agent_md(const cJSON *jsonobj,
			   rpc_trn_agent_metadata_t *agent_md)
{
	cJSON *ep = cJSON_GetObjectItem(jsonobj, "ep");
	cJSON *net = cJSON_GetObjectItem(jsonobj, "net");
	cJSON *eth = cJSON_GetObjectItem(jsonobj, "eth");
	int err_ep, err_net, err_eth;
	err_ep = trn_cli_parse_ep(ep, &agent_md->ep);
	err_net = trn_cli_parse_net(net, &agent_md->net);
	err_eth = trn_cli_parse_tun_intf(eth, &agent_md->eth);

	if (err_ep || err_net || err_eth) {
		return -EINVAL;
	}

	return 0;
}

int trn_cli_read_conf_str(ketopt_t *om, int argc, char *argv[],
			  struct cli_conf_data_t *conf)
{
	int i, c;
	if (conf == NULL) {
		return -EINVAL;
	}

	char conf_file[4096] = "";

	while ((c = ketopt(om, argc, argv, 0, "f:j:i:", 0)) >= 0) {
		if (c == 'j') {
			strcpy(conf->conf_str, om->arg);
		} else if (c == 'f') {
			strcpy(conf_file, om->arg);
		} else if (c == 'i') {
			strcpy(conf->intf, om->arg);
		}
	}

	if (conf->intf[0] == 0) {
		fprintf(stderr, "Missing interface.\n");
		return -EINVAL;
	}

	if (conf->conf_str[0] == 0 && conf_file[0] == 0) {
		fprintf(stderr,
			"Missing configuration string or configuration file.\n");
		return -EINVAL;
	}

	if (conf->conf_str[0] && conf_file[0]) {
		fprintf(stderr,
			"Either configuration string or configuration file is expected. Providing both is ambiguous.\n");
		return -EINVAL;
	}

	if (conf_file[0]) {
		printf("Reading Configuration file: %s\n", conf_file);

		FILE *f = fopen(conf_file, "rb");
		fseek(f, 0, SEEK_END);
		size_t fsize = ftell(f);
		size_t size = fsize + 1;
		fseek(f, 0, SEEK_SET);

		if (fsize > 4096 ||
		    fread(conf->conf_str, 1, fsize, f) < fsize) {
			fprintf(stderr,
				"Configuration file partially loaded.\n");
			exit(1);
		}
		fclose(f);

		conf->conf_str[fsize] = 0;
	}
	return 0;
}

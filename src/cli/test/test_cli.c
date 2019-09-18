// SPDX-License-Identifier: GPL-2.0-or-later
/**
 * @file test_cli.c
 * @author Sherif Abdelwahab (@zasherif)
 *         Phu Tran          (@phudtran)
 *
 * @brief cli unit tests
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
#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>
#include "cli/trn_cli.h"
#include "trn_log.h"
#include <stdio.h>
#include <stdbool.h>

static int clnt_perror_called = 0;

static int update_net_1_rc = 0;
static int *update_net_1_rc_ptr = &update_net_1_rc;

int *__wrap_update_vpc_1(rpc_trn_vpc_t *vpc, CLIENT *clnt)
{
	check_expected_ptr(vpc);
	check_expected_ptr(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_update_net_1(rpc_trn_network_t *net, CLIENT *clnt)
{
	check_expected_ptr(net);
	check_expected_ptr(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_update_ep_1(rpc_trn_endpoint_t *ep, CLIENT *clnt)
{
	check_expected_ptr(ep);
	check_expected_ptr(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_load_transit_xdp_1(rpc_trn_xdp_intf_t *itf, CLIENT *clnt)
{
	UNUSED(itf);
	UNUSED(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_unload_transit_xdp_1(rpc_trn_xdp_intf_t *itf, CLIENT *clnt)
{
	UNUSED(itf);
	UNUSED(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_load_transit_agent_xdp_1(rpc_trn_xdp_intf_t *itf, CLIENT *clnt)
{
	UNUSED(itf);
	UNUSED(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_unload_transit_agent_xdp_1(rpc_trn_xdp_intf_t *itf, CLIENT *clnt)
{
	UNUSED(itf);
	UNUSED(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_update_agent_ep_1(rpc_trn_endpoint_t *ep, CLIENT *clnt)
{
	check_expected_ptr(ep);
	check_expected_ptr(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

int *__wrap_update_agent_md_1(rpc_trn_agent_metadata_t *md, CLIENT *clnt)
{
	check_expected_ptr(md);
	check_expected_ptr(clnt);
	int *retval = mock_ptr_type(int *);
	function_called();
	return retval;
}

rpc_trn_vpc_t *__wrap_get_vpc_1(rpc_trn_vpc_key_t *argp, CLIENT *clnt)
{
	check_expected_ptr(argp);
	check_expected_ptr(clnt);
	rpc_trn_vpc_t *retval = mock_ptr_type(rpc_trn_vpc_t *);
	function_called();
	return retval;
}

rpc_trn_network_t *__wrap_get_net_1(rpc_trn_network_key_t *argp, CLIENT *clnt)
{
	check_expected_ptr(argp);
	check_expected_ptr(clnt);
	rpc_trn_network_t *retval = mock_ptr_type(rpc_trn_network_t *);
	function_called();
	return retval;
}

rpc_trn_endpoint_t *__wrap_get_ep_1(rpc_trn_endpoint_key_t *argp, CLIENT *clnt)
{
	check_expected_ptr(argp);
	check_expected_ptr(clnt);
	rpc_trn_endpoint_t *retval = mock_ptr_type(rpc_trn_endpoint_t *);
	function_called();
	return retval;
}

rpc_trn_endpoint_t *__wrap_get_agent_ep_1(rpc_trn_endpoint_key_t *argp,
					  CLIENT *clnt)
{
	check_expected_ptr(argp);
	check_expected_ptr(clnt);
	rpc_trn_endpoint_t *retval = mock_ptr_type(rpc_trn_endpoint_t *);
	function_called();
	return retval;
}

rpc_trn_agent_metadata_t *__wrap_get_agent_md_1(rpc_intf_t *argp, CLIENT *clnt)
{
	check_expected_ptr(argp);
	check_expected_ptr(clnt);
	rpc_trn_agent_metadata_t *retval =
		mock_ptr_type(rpc_trn_agent_metadata_t *);
	function_called();
	return retval;
}

static inline int cmpfunc(const void *a, const void *b)
{
	return (*(int *)a - *(int *)b);
}

static int check_vpc_equal(const LargestIntegralType value,
			   const LargestIntegralType check_value_data)
{
	struct rpc_trn_vpc_t *vpc = (struct rpc_trn_vpc_t *)value;
	struct rpc_trn_vpc_t *c_vpc = (struct rpc_trn_vpc_t *)check_value_data;
	int i;

	if (strcmp(vpc->interface, c_vpc->interface) != 0) {
		return false;
	}

	if (vpc->tunid != c_vpc->tunid) {
		return false;
	}

	if (vpc->routers_ips.routers_ips_len !=
	    c_vpc->routers_ips.routers_ips_len) {
		return false;
	}

	qsort(vpc->routers_ips.routers_ips_val,
	      vpc->routers_ips.routers_ips_len, sizeof(uint32_t), cmpfunc);

	qsort(c_vpc->routers_ips.routers_ips_val,
	      c_vpc->routers_ips.routers_ips_len, sizeof(uint32_t), cmpfunc);

	for (i = 0; i < vpc->routers_ips.routers_ips_len; i++) {
		if (c_vpc->routers_ips.routers_ips_val[i] !=
		    vpc->routers_ips.routers_ips_val[i])
			return false;
	}
	return true;
}

static int check_net_equal(const LargestIntegralType value,
			   const LargestIntegralType check_value_data)
{
	struct rpc_trn_network_t *net = (struct rpc_trn_network_t *)value;
	struct rpc_trn_network_t *c_net =
		(struct rpc_trn_network_t *)check_value_data;
	int i;

	if (strcmp(net->interface, c_net->interface) != 0) {
		return false;
	}

	if (net->tunid != c_net->tunid) {
		return false;
	}

	if (net->prefixlen != c_net->prefixlen) {
		return false;
	}

	if (net->netip != c_net->netip) {
		return false;
	}

	if (net->switches_ips.switches_ips_len !=
	    c_net->switches_ips.switches_ips_len) {
		return false;
	}

	qsort(net->switches_ips.switches_ips_val,
	      net->switches_ips.switches_ips_len, sizeof(uint32_t), cmpfunc);

	qsort(c_net->switches_ips.switches_ips_val,
	      c_net->switches_ips.switches_ips_len, sizeof(uint32_t), cmpfunc);

	for (i = 0; i < net->switches_ips.switches_ips_len; i++) {
		if (c_net->switches_ips.switches_ips_val[i] !=
		    net->switches_ips.switches_ips_val[i])
			return false;
	}
	return true;
}

static int check_ep_equal(const LargestIntegralType value,
			  const LargestIntegralType check_value_data)
{
	struct rpc_trn_endpoint_t *ep = (struct rpc_trn_endpoint_t *)value;
	struct rpc_trn_endpoint_t *c_ep =
		(struct rpc_trn_endpoint_t *)check_value_data;
	int i;

	if (strcmp(ep->interface, c_ep->interface) != 0) {
		return false;
	}

	if (strcmp(ep->hosted_interface, c_ep->hosted_interface) != 0) {
		return false;
	}

	if (strcmp(ep->veth, c_ep->veth) != 0) {
		return false;
	}

	if (memcmp(ep->mac, c_ep->mac, sizeof(char) * 6) != 0) {
		return false;
	}

	if (ep->ip != c_ep->ip) {
		return false;
	}

	if (ep->eptype != c_ep->eptype) {
		return false;
	}

	if (ep->tunid != c_ep->tunid) {
		return false;
	}

	if (ep->remote_ips.remote_ips_len != c_ep->remote_ips.remote_ips_len) {
		return false;
	}

	if (ep->remote_ips.remote_ips_len == 0) {
		return true;
	}

	qsort(ep->remote_ips.remote_ips_val, ep->remote_ips.remote_ips_len,
	      sizeof(uint32_t), cmpfunc);

	qsort(c_ep->remote_ips.remote_ips_val, c_ep->remote_ips.remote_ips_len,
	      sizeof(uint32_t), cmpfunc);

	for (i = 0; i < ep->remote_ips.remote_ips_len; i++) {
		if (c_ep->remote_ips.remote_ips_val[i] !=
		    ep->remote_ips.remote_ips_val[i]) {
			return false;
		}
	}

	return true;
}

static int check_md_equal(const LargestIntegralType value,
			  const LargestIntegralType check_value_data)

{
	struct rpc_trn_agent_metadata_t *md =
		(struct rpc_trn_agent_metadata_t *)value;
	struct rpc_trn_agent_metadata_t *c_md =
		(struct rpc_trn_agent_metadata_t *)check_value_data;

	if (!check_ep_equal((const LargestIntegralType)&md->ep,
			    (const LargestIntegralType)&c_md->ep)) {
		return false;
	}

	if (!check_net_equal((const LargestIntegralType)&md->net,
			     (const LargestIntegralType)&c_md->net)) {
		return false;
	}

	if (strcmp(md->eth.interface, c_md->eth.interface) != 0) {
		return false;
	}

	if (md->eth.ip != c_md->eth.ip) {
		return false;
	}

	if (memcmp(md->eth.mac, c_md->eth.mac, sizeof(char) * 6) != 0) {
		return false;
	}

	return true;
}

static int check_vpc_key_equal(const LargestIntegralType value,
			       const LargestIntegralType check_value_data)
{
	struct rpc_trn_vpc_key_t *vpc_key = (struct rpc_trn_vpc_key_t *)value;
	struct rpc_trn_vpc_key_t *c_vpc_key =
		(struct rpc_trn_vpc_key_t *)check_value_data;

	if (strcmp(vpc_key->interface, c_vpc_key->interface) != 0) {
		return false;
	}

	if (vpc_key->tunid != c_vpc_key->tunid) {
		return false;
	}

	return true;
}

static int check_net_key_equal(const LargestIntegralType value,
			       const LargestIntegralType check_value_data)
{
	struct rpc_trn_network_key_t *net_key =
		(struct rpc_trn_network_key_t *)value;
	struct rpc_trn_network_key_t *c_net_key =
		(struct rpc_trn_network_key_t *)check_value_data;

	if (strcmp(net_key->interface, c_net_key->interface) != 0) {
		return false;
	}

	if (net_key->tunid != c_net_key->tunid) {
		return false;
	}

	if (net_key->prefixlen != c_net_key->prefixlen) {
		return false;
	}

	if (net_key->netip != c_net_key->netip) {
		return false;
	}

	return true;
}

static int check_ep_key_equal(const LargestIntegralType value,
			      const LargestIntegralType check_value_data)
{
	struct rpc_trn_endpoint_key_t *ep_key =
		(struct rpc_trn_endpoint_key_t *)value;
	struct rpc_trn_endpoint_key_t *c_ep_key =
		(struct rpc_trn_endpoint_key_t *)check_value_data;

	if (strcmp(ep_key->interface, c_ep_key->interface) != 0) {
		return false;
	}

	if (ep_key->tunid != c_ep_key->tunid) {
		return false;
	}

	if (ep_key->ip != c_ep_key->ip) {
		return false;
	}

	return true;
}

static int check_md_itf_equal(const LargestIntegralType value,
			      const LargestIntegralType check_value_data)
{
	struct rpc_intf_t *md_itf = (struct rpc_intf_t *)value;
	struct rpc_intf_t *c_md_itf = (struct rpc_intf_t *)check_value_data;

	if (strcmp(md_itf->interface, c_md_itf->interface) != 0) {
		return false;
	}

	return true;
}

static void test_trn_cli_update_vpc_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int update_vpc_1_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "update-vpc", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "routers_ips": ["10.0.0.1", "10.0.0.2"]
			  }) };

	char *argv2[] = { "update-vpc", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": 3,
				  "routers_ips": ["10.0.0.1", "10.0.0.2"]
			  }) };

	char *argv3[] = { "update-vpc", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "routers_ips": [10.0.0.1, "10.0.0.2"]
			  }) };

	char itf[] = "eth0";
	uint32_t routers[] = { 0x100000a, 0x200000a };

	struct rpc_trn_vpc_t exp_vpc = {
		.interface = itf,
		.tunid = 3,
		.routers_ips = { .routers_ips_len = 2,
				 .routers_ips_val = routers }

	};

	/* Test call update_vpc successfully */
	TEST_CASE("update_vpc succeed with well formed vpc json input");
	update_vpc_1_ret_val = 0;
	expect_function_call(__wrap_update_vpc_1);
	will_return(__wrap_update_vpc_1, &update_vpc_1_ret_val);
	expect_check(__wrap_update_vpc_1, vpc, check_vpc_equal, &exp_vpc);
	expect_any(__wrap_update_vpc_1, clnt);
	rc = trn_cli_update_vpc_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse vpc input error*/
	TEST_CASE("update_vpc is not called with non-string field");
	rc = trn_cli_update_vpc_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	/* Test parse vpc input error 2*/
	TEST_CASE("update_vpc is not called malformed json");
	rc = trn_cli_update_vpc_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_vpc_1 return error*/
	TEST_CASE("update-vpc subcommand fails if update_vpc_1 returns error");
	update_vpc_1_ret_val = -EINVAL;
	expect_function_call(__wrap_update_vpc_1);
	will_return(__wrap_update_vpc_1, &update_vpc_1_ret_val);
	expect_any(__wrap_update_vpc_1, vpc);
	expect_any(__wrap_update_vpc_1, clnt);
	rc = trn_cli_update_vpc_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_vpc_1 return NULL*/
	TEST_CASE("update-vpc subcommand fails if update_vpc_1 returns NULl");
	expect_function_call(__wrap_update_vpc_1);
	will_return(__wrap_update_vpc_1, NULL);
	expect_any(__wrap_update_vpc_1, vpc);
	expect_any(__wrap_update_vpc_1, clnt);
	rc = trn_cli_update_vpc_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_update_net_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int update_net_1_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "update-net", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "nip": "10.0.0.0",
				  "prefixlen": "16",
				  "switches_ips": ["10.0.0.1", "10.0.0.2"]
			  }) };

	char *argv2[] = { "update-net", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": 3,
				  "nip": "10.0.0.0",
				  "prefixlen": "16",
				  "switches_ips": ["10.0.0.1", "10.0.0.2"]
			  }) };

	char *argv3[] = { "update-net", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "nip": "adsfwef",
				  "prefixlen": "16",
				  "switches_ips": [10.0.0.1, "10.0.0.2"]
			  }) };

	char itf[] = "eth0";
	uint32_t switches[] = { 0x100000a, 0x200000a };

	struct rpc_trn_network_t exp_net = {
		.interface = itf,
		.prefixlen = 16,
		.tunid = 3,
		.netip = 0xa,
		.switches_ips = { .switches_ips_len = 2,
				  .switches_ips_val = switches }
	};

	/* Test call update_net successfully */
	TEST_CASE("update_net succeed with well formed network json input");
	update_net_1_ret_val = 0;
	expect_function_call(__wrap_update_net_1);
	will_return(__wrap_update_net_1, &update_net_1_ret_val);
	expect_check(__wrap_update_net_1, net, check_net_equal, &exp_net);
	expect_any(__wrap_update_net_1, clnt);
	rc = trn_cli_update_net_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse net input error*/
	TEST_CASE("update_net is not called with non-string field");
	rc = trn_cli_update_net_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	/* Test parse net input error 2*/
	TEST_CASE("update_net is not called malformed json");
	rc = trn_cli_update_net_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_net_1 return error*/
	TEST_CASE("update-net subcommand fails if update_net_1 returns error");
	update_net_1_ret_val = -EINVAL;
	expect_function_call(__wrap_update_net_1);
	will_return(__wrap_update_net_1, &update_net_1_ret_val);
	expect_any(__wrap_update_net_1, net);
	expect_any(__wrap_update_net_1, clnt);
	rc = trn_cli_update_net_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_net_1 return NULL*/
	TEST_CASE("update-net subcommand fails if update_net_1 returns NULl");
	expect_function_call(__wrap_update_net_1);
	will_return(__wrap_update_net_1, NULL);
	expect_any(__wrap_update_net_1, net);
	expect_any(__wrap_update_net_1, clnt);
	rc = trn_cli_update_net_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_update_ep_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int update_ep_1_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "update-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "ip": "10.0.0.1",
				  "eptype": "1",
				  "mac": "1:2:3:4:5:6",
				  "veth": "veth0",
				  "remote_ips": ["10.0.0.2"],
				  "hosted_iface": "peer"
			  }) };

	char *argv2[] = { "update-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": 3,
				  "ip": "10.0.0.1",
				  "eptype": "1",
				  "mac": "1:2:3:4:5:6",
				  "veth": "veth0",
				  "remote_ips": ["10.0.0.2"],
				  "hosted_iface": "peer"
			  }) };

	char *argv3[] = { "update-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "mac": "1:2:3:4:5:6",
				  "veth": "veth0",
				  "remote_ips": ["10.0.0.2"],
				  "hosted_iface": "peer"
			  }) };

	char *argv4[] = { "update-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "mac": "1:2:3:4:5:6",
				  "veth": "veth0",
				  "remote_ips": [10.0.0.2],
				  "hosted_iface": "peer"
			  }) };

	char itf[] = "eth0";
	char vitf[] = "veth0";
	char hosted_itf[] = "peer";
	uint32_t remote[] = { 0x200000a };
	char mac[6] = { 1, 2, 3, 4, 5, 6 };

	struct rpc_trn_endpoint_t exp_ep = {
		.interface = itf,
		.ip = 0x100000a,
		.eptype = 1,
		.remote_ips = { .remote_ips_len = 1, .remote_ips_val = remote },
		.hosted_interface = hosted_itf,
		.veth = vitf,
		.tunid = 3,
	};

	memcpy(exp_ep.mac, mac, sizeof(char) * 6);

	/* Test call update_ep successfully */
	TEST_CASE("update_ep succeed with well formed endpoint json input");
	update_ep_1_ret_val = 0;
	expect_function_call(__wrap_update_ep_1);
	will_return(__wrap_update_ep_1, &update_ep_1_ret_val);
	expect_check(__wrap_update_ep_1, ep, check_ep_equal, &exp_ep);
	expect_any(__wrap_update_ep_1, clnt);
	rc = trn_cli_update_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse ep input error*/
	TEST_CASE("update_ep is not called with non-string field");
	rc = trn_cli_update_ep_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("update_ep is not called with missing required field");
	rc = trn_cli_update_ep_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test parse ep input error 2*/
	TEST_CASE("update_ep is not called malformed json");
	rc = trn_cli_update_ep_subcmd(NULL, argc, argv4);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_ep_1 return error*/
	TEST_CASE("update-ep subcommand fails if update_ep_1 returns error");
	update_ep_1_ret_val = -EINVAL;
	expect_function_call(__wrap_update_ep_1);
	will_return(__wrap_update_ep_1, &update_ep_1_ret_val);
	expect_any(__wrap_update_ep_1, ep);
	expect_any(__wrap_update_ep_1, clnt);
	rc = trn_cli_update_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_ep_1 return NULL*/
	TEST_CASE("update-ep subcommand fails if update_ep_1 returns NULl");
	expect_function_call(__wrap_update_ep_1);
	will_return(__wrap_update_ep_1, NULL);
	expect_any(__wrap_update_ep_1, ep);
	expect_any(__wrap_update_ep_1, clnt);
	rc = trn_cli_update_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_load_transit_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int load_transit_xdp_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "load-transit-xdp", "-i", "eth0", "-j", QUOTE({
				  "xdp_path": "/path/to/xdp/object/file",
				  "pcapfile": "/path/to/bpf/pinned/map"
			  }) };

	char *argv2[] = { "load-transit-xdp", "-i", "eth0", "-j",
			  QUOTE({ "pcapfile": "/path/to/bpf/pinned/map" }) };

	char *argv3[] = { "load-transit-xdp", "-i", "eth0", "-j",
			  QUOTE({ "xdp_path": "/path/to/xdp/object/file" }) };

	/* Test call load_transit_xdp_1 successfully */
	TEST_CASE("load_transit_xdp succeed with well formed input");
	load_transit_xdp_ret_val = 0;
	expect_function_call(__wrap_load_transit_xdp_1);
	will_return(__wrap_load_transit_xdp_1, &load_transit_xdp_ret_val);
	rc = trn_cli_load_transit_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	TEST_CASE("load_transit_xdp fails if path to object file is missing");
	rc = trn_cli_load_transit_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("load_transit_xdp succeed even if pcap map is missing");
	load_transit_xdp_ret_val = 0;
	expect_function_call(__wrap_load_transit_xdp_1);
	will_return(__wrap_load_transit_xdp_1, &load_transit_xdp_ret_val);
	rc = trn_cli_load_transit_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, 0);

	TEST_CASE("load_transit_xdp fails if rpc returns Error");
	load_transit_xdp_ret_val = -EINVAL;
	expect_function_call(__wrap_load_transit_xdp_1);
	will_return(__wrap_load_transit_xdp_1, &load_transit_xdp_ret_val);
	rc = trn_cli_load_transit_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test call load_transit_xdp return NULL*/
	TEST_CASE("load_transit_xdp subcommand fails if rpc returns NULl");
	expect_function_call(__wrap_load_transit_xdp_1);
	will_return(__wrap_load_transit_xdp_1, NULL);
	rc = trn_cli_load_transit_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_unload_transit_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int unload_transit_xdp_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "load-transit-xdp", "-i", "eth0", "-j", QUOTE({}) };

	/* Test call unload_transit_xdp_1 successfully */
	TEST_CASE("unload_transit_xdp succeed with well formed (empty) input");
	unload_transit_xdp_ret_val = 0;
	expect_function_call(__wrap_unload_transit_xdp_1);
	will_return(__wrap_unload_transit_xdp_1, &unload_transit_xdp_ret_val);
	rc = trn_cli_unload_transit_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test call unload_transit_xdp return error*/
	TEST_CASE(
		"unload_transit_xdp subcommand fails if update_net_1 returns error");
	unload_transit_xdp_ret_val = -EINVAL;
	expect_function_call(__wrap_unload_transit_xdp_1);
	will_return(__wrap_unload_transit_xdp_1, &unload_transit_xdp_ret_val);
	rc = trn_cli_unload_transit_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call unload_transit_xdp_! return NULL*/
	TEST_CASE("unload_transit_xdp subcommand fails if rpc returns NULl");
	expect_function_call(__wrap_unload_transit_xdp_1);
	will_return(__wrap_unload_transit_xdp_1, NULL);
	rc = trn_cli_unload_transit_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_load_agent_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int load_agent_xdp_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "load-agent-xdp", "-i", "eth0", "-j", QUOTE({
				  "xdp_path": "/path/to/xdp/object/file",
				  "pcapfile": "/path/to/bpf/pinned/map"
			  }) };

	char *argv2[] = { "load-agent-xdp", "-i", "eth0", "-j",
			  QUOTE({ "pcapfile": "/path/to/bpf/pinned/map" }) };

	char *argv3[] = { "load-agent-xdp", "-i", "eth0", "-j",
			  QUOTE({ "xdp_path": "/path/to/xdp/object/file" }) };

	/* Test call load_transit_xdp_1 successfully */
	TEST_CASE("load_agent_xdp succeed with well formed input");
	load_agent_xdp_ret_val = 0;
	expect_function_call(__wrap_load_transit_agent_xdp_1);
	will_return(__wrap_load_transit_agent_xdp_1, &load_agent_xdp_ret_val);
	rc = trn_cli_load_agent_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	TEST_CASE("load_agent_xdp fails if path to object file is missing");
	rc = trn_cli_load_agent_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("load_agent_xdp succeed even if pcap map is missing");
	load_agent_xdp_ret_val = 0;
	expect_function_call(__wrap_load_transit_agent_xdp_1);
	will_return(__wrap_load_transit_agent_xdp_1, &load_agent_xdp_ret_val);
	rc = trn_cli_load_agent_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, 0);

	TEST_CASE("load_agent_xdp fails if rpc returns Error");
	load_agent_xdp_ret_val = -EINVAL;
	expect_function_call(__wrap_load_transit_agent_xdp_1);
	will_return(__wrap_load_transit_agent_xdp_1, &load_agent_xdp_ret_val);
	rc = trn_cli_load_agent_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test call load_transit_xdp return NULL*/
	TEST_CASE("load_agent_xdp subcommand fails if rpc returns NULl");
	expect_function_call(__wrap_load_transit_agent_xdp_1);
	will_return(__wrap_load_transit_agent_xdp_1, NULL);
	rc = trn_cli_load_agent_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_unload_agent_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int unload_transit_xdp_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "unload-agent-xdp", "-i", "eth0", "-j", QUOTE({}) };

	/* Test call unload_agent_xdp_1 successfully */
	TEST_CASE("unload_agent_xdp succeed with well formed (empty) input");
	unload_transit_xdp_ret_val = 0;
	expect_function_call(__wrap_unload_transit_agent_xdp_1);
	will_return(__wrap_unload_transit_agent_xdp_1,
		    &unload_transit_xdp_ret_val);
	rc = trn_cli_unload_agent_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test call unload_agent_xdp return error*/
	TEST_CASE(
		"unload_tagent_xdp subcommand fails if update_net_1 returns error");
	unload_transit_xdp_ret_val = -EINVAL;
	expect_function_call(__wrap_unload_transit_agent_xdp_1);
	will_return(__wrap_unload_transit_agent_xdp_1,
		    &unload_transit_xdp_ret_val);
	rc = trn_cli_unload_agent_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call unload_agent_xdp return NULL*/
	TEST_CASE("unload_agent_xdp subcommand fails if rpc returns NULl");
	expect_function_call(__wrap_unload_transit_agent_xdp_1);
	will_return(__wrap_unload_transit_agent_xdp_1, NULL);
	rc = trn_cli_unload_agent_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_update_agent_ep_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;
	int update_agent_ep_1_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "update-agent-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "0",
				  "ip": "10.0.0.1",
				  "eptype": "0",
				  "mac": "1:2:3:4:5:6",
				  "veth": "",
				  "remote_ips": [],
				  "hosted_iface": ""
			  }) };

	char *argv2[] = { "update-agent-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": 0,
				  "ip": "10.0.0.1",
				  "eptype": "0",
				  "mac": "1:2:3:4:5:6",
				  "veth": "",
				  "remote_ips": [],
				  "hosted_iface": ""
			  }) };

	char *argv3[] = { "update-agent-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "0",
				  "mac": "1:2:3:4:5:6",
				  "veth": "",
				  "remote_ips": [],
				  "hosted_iface": ""
			  }) };

	char *argv4[] = { "update-agent-ep", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "0",
				  "ip": "10.0.0.1",
				  "eptype": "0",
				  "mac": "1:2:3:4:5:6",
				  "veth":,
				  "remote_ips": [],
				  "hosted_iface": ""
			  }) };

	char itf[] = "eth0";
	char vitf[] = "";
	char hosted_itf[] = "";
	char mac[6] = { 1, 2, 3, 4, 5, 6 };

	struct rpc_trn_endpoint_t exp_ep = {
		.interface = itf,
		.ip = 0x100000a,
		.eptype = 0,
		.remote_ips = { .remote_ips_len = 0 },
		.hosted_interface = hosted_itf,
		.veth = vitf,
		.tunid = 0,
	};

	memcpy(exp_ep.mac, mac, sizeof(char) * 6);

	/* Test call update_agent_ep successfully */
	TEST_CASE(
		"update_agent_ep succeed with well formed endpoint json input");
	update_agent_ep_1_ret_val = 0;
	expect_function_call(__wrap_update_agent_ep_1);
	will_return(__wrap_update_agent_ep_1, &update_agent_ep_1_ret_val);
	expect_check(__wrap_update_agent_ep_1, ep, check_ep_equal, &exp_ep);
	expect_any(__wrap_update_agent_ep_1, clnt);
	rc = trn_cli_update_agent_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse ep input error*/
	TEST_CASE("update_agent_ep is not called with non-string field");
	rc = trn_cli_update_agent_ep_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("update_agent_ep is not called with missing required field");
	rc = trn_cli_update_agent_ep_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test parse ep input error 2*/
	TEST_CASE("update_agent_ep is not called malformed json");
	rc = trn_cli_update_agent_ep_subcmd(NULL, argc, argv4);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_ep_1 return error*/
	TEST_CASE(
		"update_agent_ep subcommand fails if update_net_1 returns error");
	update_agent_ep_1_ret_val = -EINVAL;
	expect_function_call(__wrap_update_agent_ep_1);
	will_return(__wrap_update_agent_ep_1, &update_agent_ep_1_ret_val);
	expect_any(__wrap_update_agent_ep_1, ep);
	expect_any(__wrap_update_agent_ep_1, clnt);
	rc = trn_cli_update_agent_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call update_ep_1 return NULL*/
	TEST_CASE(
		"update_agent_ep subcommand fails if update_ep_1 returns NULl");
	expect_function_call(__wrap_update_agent_ep_1);
	will_return(__wrap_update_agent_ep_1, NULL);
	expect_any(__wrap_update_agent_ep_1, ep);
	expect_any(__wrap_update_agent_ep_1, clnt);
	rc = trn_cli_update_agent_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_update_agent_md_subcmd(void **state)
{
	UNUSED(state);

	int rc;
	int argc = 5;
	int update_agent_md_1_ret_val = 0;

	/* Test cases */
	char *argv1[] = { "update-agent-metadata", "-i", "eth0", "-j", QUOTE({
				  "ep": {
					  "tunnel_id": "3",
					  "ip": "10.0.0.1",
					  "eptype": "1",
					  "mac": "1:2:3:4:5:6",
					  "veth": "veth0",
					  "remote_ips": ["10.0.0.2"],
					  "hosted_iface": "eth0"
				  },
				  "net": {
					  "tunnel_id": "3",
					  "nip": "10.0.0.0",
					  "prefixlen": "16",
					  "switches_ips":
						  ["10.0.0.1", "10.0.0.2"]
				  },
				  "eth": {
					  "ip": "10.0.0.1",
					  "mac": "6:5:4:3:2:1",
					  "iface": "eth0"
				  }
			  }) };

	char *argv2[] = {
		"update-agent-metadata", "-i", "eth0", "-j", QUOTE({
			"ep": {
				"tunnel_id": "3",
				"ip": "10.0.0.1",
				"eptype": "1",
				"mac": "1:2:3:4:5:6",
				"veth": "veth0",
				"remote_ips": ["10.0.0.2"],
				"hosted_iface": "eth0"
			},
			"net": {
				"tunnel_id": "3",
				"nip": "10.0.0.0",
				"prefixlen": "16",
				"switches_ips": ["10.0.0.1", "10.0.0.2"]
			},
			"eth": { "ip": "10.0.0.1", "mac": "6:5:4:3:2:1" }
		})
	};

	char *argv3[] = { "update-agent-metadata", "-i", "eth0", "-j", QUOTE({
				  "ep": {
					  "tunnel_id": "3",
					  "ip": "10.0.0.1",
					  "eptype": "1",
					  "mac": "1:2:3:4:5:6",
					  "veth": "veth0",
					  "remote_ips": ["10.0.0.2"],
					  "hosted_iface": "eth0"
				  },
				  "net": {
					  "tunnel_id": "3",
					  "nip": "10.0.0.0",
					  "prefixlen": "16",
					  "switches_ips":
						  ["10.0.0.1", "10.0.0.2"]
				  },
				  "eth": {
					  "ip": "10.0.0.1",
					  "mac": "6:5:4:3:2:1",
					  "iface": eth0
				  }
			  }) };

	char itf[] = "eth0";
	char vitf[] = "veth0";
	char hosted_itf[] = "eth0";
	uint32_t remote[] = { 0x200000a };
	uint32_t switches[] = { 0x100000a, 0x200000a };
	char mac[6] = { 1, 2, 3, 4, 5, 6 };
	char mac_eth[6] = { 6, 5, 4, 3, 2, 1 };

	struct rpc_trn_agent_metadata_t exp_md = {
		.interface = itf,
		.ep = { .interface = itf,
			.ip = 0x100000a,
			.eptype = 1,
			.hosted_interface = hosted_itf,
			.veth = vitf,
			.tunid = 3,
			.remote_ips = { .remote_ips_len = 1,
					.remote_ips_val = remote } },
		.net = { .interface = itf,
			 .prefixlen = 16,
			 .tunid = 3,
			 .netip = 0xa,
			 .switches_ips = { .switches_ips_len = 2,
					   .switches_ips_val = switches } },
		.eth = { .interface = itf, .ip = 0x100000a }
	};

	memcpy(exp_md.ep.mac, mac, sizeof(char) * 6);
	memcpy(exp_md.eth.mac, mac_eth, sizeof(char) * 6);

	TEST_CASE(
		"update_agent_md succeed with well formed agent metadata json input");
	update_agent_md_1_ret_val = 0;
	expect_function_call(__wrap_update_agent_md_1);
	will_return(__wrap_update_agent_md_1, &update_agent_md_1_ret_val);
	expect_check(__wrap_update_agent_md_1, md, check_md_equal, &exp_md);
	expect_any(__wrap_update_agent_md_1, clnt);
	rc = trn_cli_update_agent_md_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	TEST_CASE("update_agent_md is not called with missing eth0 field");
	rc = trn_cli_update_agent_md_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("update_agent_md is not called is not called malformed json");
	rc = trn_cli_update_agent_md_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("update_agent_md subcommand fails if rpc returns error");
	update_agent_md_1_ret_val = -EINVAL;
	expect_function_call(__wrap_update_agent_md_1);
	will_return(__wrap_update_agent_md_1, &update_agent_md_1_ret_val);
	expect_check(__wrap_update_agent_md_1, md, check_md_equal, &exp_md);
	expect_any(__wrap_update_agent_md_1, clnt);
	rc = trn_cli_update_agent_md_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("update_agent_md subcommand fails if rpc returns NULl");
	expect_function_call(__wrap_update_agent_md_1);
	will_return(__wrap_update_agent_md_1, NULL);
	expect_check(__wrap_update_agent_md_1, md, check_md_equal, &exp_md);
	expect_any(__wrap_update_agent_md_1, clnt);
	rc = trn_cli_update_agent_md_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_get_vpc_subcmd(void **state)
{
	UNUSED(state);
	rpc_trn_vpc_t return_vpc;
	int argc = 5;
	int rc;

	char itf[] = "eth0";
	uint32_t routers[] = { 0x100000a, 0x200000a };
	struct rpc_trn_vpc_t get_vpc_1_ret_val = {
		.interface = itf,
		.tunid = 3,
		.routers_ips = { .routers_ips_len = 2,
				 .routers_ips_val = routers }
	};

	struct rpc_trn_vpc_key_t exp_vpc_key = {
		.interface = itf,
		.tunid = 3,
	};
	/* Test cases */
	char *argv1[] = { "get-vpc", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": "3" }) };

	char *argv2[] = { "get-vpc", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": 3 }) };

	char *argv3[] = { "get-vpc", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id: 3" }) };

	/* Test call get_vpc successfully */
	TEST_CASE("get_vpc succeed with well formed vpc json input");
	expect_function_call(__wrap_get_vpc_1);
	will_return(__wrap_get_vpc_1, &get_vpc_1_ret_val);
	expect_check(__wrap_get_vpc_1, argp, check_vpc_key_equal, &exp_vpc_key);
	expect_any(__wrap_get_vpc_1, clnt);
	rc = trn_cli_get_vpc_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse vpc input error*/
	TEST_CASE("get_vpc is not called with non-string field");
	rc = trn_cli_get_vpc_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	/* Test parse vpc input error 2*/
	TEST_CASE("get_vpc is not called malformed json");
	rc = trn_cli_get_vpc_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_vpc_1 return error*/
	TEST_CASE(
		"get-vpc subcommand fails if get_vpc_1 returns empty string interface");
	get_vpc_1_ret_val.interface = "";
	expect_function_call(__wrap_get_vpc_1);
	will_return(__wrap_get_vpc_1, &get_vpc_1_ret_val);
	expect_any(__wrap_get_vpc_1, argp);
	expect_any(__wrap_get_vpc_1, clnt);
	rc = trn_cli_get_vpc_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_vpc_1 return NULL*/
	TEST_CASE("get-vpc subcommand fails if get_vpc_1 returns NULl");
	expect_function_call(__wrap_get_vpc_1);
	will_return(__wrap_get_vpc_1, NULL);
	expect_any(__wrap_get_vpc_1, argp);
	expect_any(__wrap_get_vpc_1, clnt);
	rc = trn_cli_get_vpc_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_get_net_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;

	char itf[] = "eth0";
	uint32_t switches[] = { 0x100000a, 0x200000a };
	struct rpc_trn_network_t get_net_1_ret_val = {
		.interface = itf,
		.prefixlen = 16,
		.tunid = 3,
		.netip = 0xa,
		.switches_ips = { .switches_ips_len = 2,
				  .switches_ips_val = switches }
	};

	/* Test cases */
	char *argv1[] = { "get-net", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "nip": "10.0.0.0",
				  "prefixlen": "16"
			  }) };

	char *argv2[] = { "get-net", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": 3,
				  "nip": "10.0.0.0",
				  "prefixlen": "16"
			  }) };

	char *argv3[] = { "get-net", "-i", "eth0", "-j", QUOTE({
				  "tunnel_id": "3",
				  "nip": "adsfwef",
				  "prefixlen: 16"
			  }) };

	struct rpc_trn_network_key_t exp_net_key = {
		.interface = itf,
		.prefixlen = 16,
		.tunid = 3,
		.netip = 0xa,
	};

	/* Test call get_net successfully */
	TEST_CASE("get_net succeed with well formed network json input");
	expect_function_call(__wrap_get_net_1);
	will_return(__wrap_get_net_1, &get_net_1_ret_val);
	expect_check(__wrap_get_net_1, argp, check_net_key_equal, &exp_net_key);
	expect_any(__wrap_get_net_1, clnt);
	rc = trn_cli_get_net_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse net key input error*/
	TEST_CASE("get_net is not called with non-string field");
	rc = trn_cli_get_net_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	/* Test parse net key input error 2*/
	TEST_CASE("get_net is not called malformed json");
	rc = trn_cli_get_net_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_net_1 return error*/
	TEST_CASE(
		"get-net subcommand fails if get_net_1 returns empty string interface");
	get_net_1_ret_val.interface = "";
	expect_function_call(__wrap_get_net_1);
	will_return(__wrap_get_net_1, &get_net_1_ret_val);
	expect_any(__wrap_get_net_1, argp);
	expect_any(__wrap_get_net_1, clnt);
	rc = trn_cli_get_net_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_net_1 return NULL*/
	TEST_CASE("get-net subcommand fails if get_net_1 returns NULl");
	expect_function_call(__wrap_get_net_1);
	will_return(__wrap_get_net_1, NULL);
	expect_any(__wrap_get_net_1, argp);
	expect_any(__wrap_get_net_1, clnt);
	rc = trn_cli_get_net_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_get_ep_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;

	char itf[] = "eth0";
	char vitf[] = "veth0";
	char hosted_itf[] = "peer";
	uint32_t remote[] = { 0x200000a };
	char mac[6] = { 1, 2, 3, 4, 5, 6 };

	struct rpc_trn_endpoint_t get_ep_1_ret_val = {
		.interface = itf,
		.ip = 0x100000a,
		.eptype = 1,
		.remote_ips = { .remote_ips_len = 1, .remote_ips_val = remote },
		.hosted_interface = hosted_itf,
		.veth = vitf,
		.tunid = 3,
	};
	memcpy(get_ep_1_ret_val.mac, mac, sizeof(char) * 6);

	/* Test cases */
	char *argv1[] = { "get-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": "3", "ip": "10.0.0.1" }) };

	char *argv2[] = { "get-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": 3, "ip": "10.0.0.1" }) };

	char *argv3[] = { "get-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": "3" }) };

	char *argv4[] = { "get-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": "3", "ip": [10.0.0.2] }) };

	struct rpc_trn_endpoint_key_t exp_ep_key = {
		.interface = itf,
		.ip = 0x100000a,
		.tunid = 3,
	};

	/* Test call get_ep successfully */
	TEST_CASE("get_ep succeed with well formed endpoint json input");
	expect_function_call(__wrap_get_ep_1);
	will_return(__wrap_get_ep_1, &get_ep_1_ret_val);
	expect_check(__wrap_get_ep_1, argp, check_ep_key_equal, &exp_ep_key);
	expect_any(__wrap_get_ep_1, clnt);
	rc = trn_cli_get_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse ep input error*/
	TEST_CASE("get_ep is not called with non-string field");
	rc = trn_cli_get_ep_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("get_ep is not called with missing required field");
	rc = trn_cli_get_ep_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test parse ep input error 2*/
	TEST_CASE("get_ep is not called malformed json");
	rc = trn_cli_get_ep_subcmd(NULL, argc, argv4);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_ep_1 return error*/
	TEST_CASE(
		"get-ep subcommand fails if get_ep_1 returns empty string interface");
	get_ep_1_ret_val.interface = "";
	expect_function_call(__wrap_get_ep_1);
	will_return(__wrap_get_ep_1, &get_ep_1_ret_val);
	expect_any(__wrap_get_ep_1, argp);
	expect_any(__wrap_get_ep_1, clnt);
	rc = trn_cli_get_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_ep_1 return NULL*/
	TEST_CASE("get-ep subcommand fails if get_ep_1 returns NULl");
	expect_function_call(__wrap_get_ep_1);
	will_return(__wrap_get_ep_1, NULL);
	expect_any(__wrap_get_ep_1, argp);
	expect_any(__wrap_get_ep_1, clnt);
	rc = trn_cli_get_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_get_agent_ep_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;

	char itf[] = "eth0";
	char vitf[] = "veth0";
	char hosted_itf[] = "peer";
	uint32_t remote[] = { 0x200000a };
	char mac[6] = { 1, 2, 3, 4, 5, 6 };

	struct rpc_trn_endpoint_t get_agent_ep_1_ret_val = {
		.interface = itf,
		.ip = 0x100000a,
		.eptype = 1,
		.remote_ips = { .remote_ips_len = 1, .remote_ips_val = remote },
		.hosted_interface = hosted_itf,
		.veth = vitf,
		.tunid = 3,
	};
	memcpy(get_agent_ep_1_ret_val.mac, mac, sizeof(char) * 6);

	/* Test cases */
	char *argv1[] = { "get-agent-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": "3", "ip": "10.0.0.1" }) };

	char *argv2[] = { "get-agent-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": 3, "ip": "10.0.0.1" }) };

	char *argv3[] = { "get-agent-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": "3" }) };

	char *argv4[] = { "get-agent-ep", "-i", "eth0", "-j",
			  QUOTE({ "tunnel_id": "3", "ip": [10.0.0.2] }) };

	struct rpc_trn_endpoint_key_t exp_agent_ep_key = {
		.interface = itf,
		.ip = 0x100000a,
		.tunid = 3,
	};

	/* Test call get_agent_ep successfully */
	TEST_CASE("get_agent_ep succeed with well formed endpoint json input");
	expect_function_call(__wrap_get_agent_ep_1);
	will_return(__wrap_get_agent_ep_1, &get_agent_ep_1_ret_val);
	expect_check(__wrap_get_agent_ep_1, argp, check_ep_key_equal,
		     &exp_agent_ep_key);
	expect_any(__wrap_get_agent_ep_1, clnt);
	rc = trn_cli_get_agent_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	/* Test parse ep input error*/
	TEST_CASE("get_agent_ep is not called with non-string field");
	rc = trn_cli_get_agent_ep_subcmd(NULL, argc, argv2);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("get_agent_ep is not called with missing required field");
	rc = trn_cli_get_agent_ep_subcmd(NULL, argc, argv3);
	assert_int_equal(rc, -EINVAL);

	/* Test parse ep input error 2*/
	TEST_CASE("get_agent_ep is not called malformed json");
	rc = trn_cli_get_agent_ep_subcmd(NULL, argc, argv4);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_ep_1 return error*/
	TEST_CASE(
		"get_agent_ep subcommand fails if get_ep_1 returns empty string interface");
	get_agent_ep_1_ret_val.interface = "";
	expect_function_call(__wrap_get_agent_ep_1);
	will_return(__wrap_get_agent_ep_1, &get_agent_ep_1_ret_val);
	expect_any(__wrap_get_agent_ep_1, argp);
	expect_any(__wrap_get_agent_ep_1, clnt);
	rc = trn_cli_get_agent_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	/* Test call get_agent_ep_1 return NULL*/
	TEST_CASE("get_agent_ep subcommand fails if get_ep_1 returns NULl");
	expect_function_call(__wrap_get_agent_ep_1);
	will_return(__wrap_get_agent_ep_1, NULL);
	expect_any(__wrap_get_agent_ep_1, argp);
	expect_any(__wrap_get_agent_ep_1, clnt);
	rc = trn_cli_get_agent_ep_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

static void test_trn_cli_get_agent_md_subcmd(void **state)
{
	UNUSED(state);
	int rc;
	int argc = 5;

	char itf[] = "eth0";
	char vitf[] = "veth0";
	char hosted_itf[] = "eth0";
	uint32_t remote[] = { 0x200000a };
	uint32_t switches[] = { 0x100000a, 0x200000a };
	char mac[6] = { 1, 2, 3, 4, 5, 6 };
	char mac_eth[6] = { 6, 5, 4, 3, 2, 1 };
	struct rpc_trn_agent_metadata_t get_agent_md_1_ret_val = {
		.interface = itf,
		.ep = { .interface = itf,
			.ip = 0x100000a,
			.eptype = 1,
			.hosted_interface = hosted_itf,
			.veth = vitf,
			.tunid = 3,
			.remote_ips = { .remote_ips_len = 1,
					.remote_ips_val = remote } },
		.net = { .interface = itf,
			 .prefixlen = 16,
			 .tunid = 3,
			 .netip = 0xa,
			 .switches_ips = { .switches_ips_len = 2,
					   .switches_ips_val = switches } },
		.eth = { .interface = itf, .ip = 0x100000a }
	};
	memcpy(get_agent_md_1_ret_val.ep.mac, mac, sizeof(char) * 6);
	memcpy(get_agent_md_1_ret_val.eth.mac, mac_eth, sizeof(char) * 6);

	/* Test cases */
	char *argv1[] = { "get-agent-metadata", "-i", "eth0", "-j", QUOTE({
				  "": "",
			  }) };

	rpc_intf_t exp_md_itf = { .interface = itf };

	TEST_CASE(
		"get_agent_md succeed with well formed agent metadata json input");
	expect_function_call(__wrap_get_agent_md_1);
	will_return(__wrap_get_agent_md_1, &get_agent_md_1_ret_val);
	expect_check(__wrap_get_agent_md_1, argp, check_md_itf_equal,
		     &exp_md_itf);
	expect_any(__wrap_get_agent_md_1, clnt);
	rc = trn_cli_get_agent_md_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, 0);

	TEST_CASE(
		"get_agent_md subcommand fails if rpc returns empty string interfac");
	get_agent_md_1_ret_val.interface = "";
	expect_function_call(__wrap_get_agent_md_1);
	will_return(__wrap_get_agent_md_1, &get_agent_md_1_ret_val);
	expect_check(__wrap_get_agent_md_1, argp, check_md_itf_equal,
		     &exp_md_itf);
	expect_any(__wrap_get_agent_md_1, clnt);
	rc = trn_cli_get_agent_md_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);

	TEST_CASE("get_agent_md subcommand fails if rpc returns NULl");
	expect_function_call(__wrap_get_agent_md_1);
	will_return(__wrap_get_agent_md_1, NULL);
	expect_check(__wrap_get_agent_md_1, argp, check_md_itf_equal,
		     &exp_md_itf);
	expect_any(__wrap_get_agent_md_1, clnt);
	rc = trn_cli_get_agent_md_subcmd(NULL, argc, argv1);
	assert_int_equal(rc, -EINVAL);
}

int main()
{
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(test_trn_cli_update_vpc_subcmd),
		cmocka_unit_test(test_trn_cli_update_net_subcmd),
		cmocka_unit_test(test_trn_cli_update_ep_subcmd),
		cmocka_unit_test(test_trn_cli_load_transit_subcmd),
		cmocka_unit_test(test_trn_cli_unload_transit_subcmd),
		cmocka_unit_test(test_trn_cli_load_agent_subcmd),
		cmocka_unit_test(test_trn_cli_unload_agent_subcmd),
		cmocka_unit_test(test_trn_cli_update_agent_ep_subcmd),
		cmocka_unit_test(test_trn_cli_update_agent_md_subcmd),
		cmocka_unit_test(test_trn_cli_get_vpc_subcmd),
		cmocka_unit_test(test_trn_cli_get_net_subcmd),
		cmocka_unit_test(test_trn_cli_get_ep_subcmd),
		cmocka_unit_test(test_trn_cli_get_agent_ep_subcmd),
		cmocka_unit_test(test_trn_cli_get_agent_md_subcmd)
	};
	return cmocka_run_group_tests(tests, NULL, NULL);
}

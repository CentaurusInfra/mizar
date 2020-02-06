# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab  <@zasherif>
#          Haibin Michael Xie <@haibinxie>
#          Phu Tran           <@phudtran>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.common import logger
from time import sleep
from scapy.all import rdpcap, IP, ARP, ICMP, TCP, UDP, Raw
from scapy.contrib.geneve import GENEVE


def do_ping_test(test, ep1, ep2, both_ways=True):
    logger.info("Test {}: {} do ping test {}".format(
        type(test).__name__, "="*10, "="*10))
    logger.info("Test: {} can ping {}".format(ep1.ip, ep2.ip))
    exit_code = ep1.do_ping(ep2.ip)[0]
    test.assertEqual(exit_code, 0)
    if both_ways:
        logger.info("Test: {} can ping {}".format(ep2.ip, ep1.ip))
        exit_code = ep2.do_ping(ep1.ip)[0]
        test.assertEqual(exit_code, 0)


def do_ping_fail_test(test, ep1, ep2, both_ways=True):
    logger.info("Test {}: {} do ping FAIL test {}".format(
        type(test).__name__, "="*10, "="*10))
    logger.info("Test: {} can NOT ping {}".format(ep2.ip, ep1.ip))
    exit_code = ep2.do_ping(ep1.ip)[0]
    test.assertNotEqual(exit_code, 0)
    if both_ways:
        logger.info("Test: {} can NOT ping {}".format(ep1.ip, ep2.ip))
        exit_code = ep1.do_ping(ep2.ip)[0]
        test.assertNotEqual(exit_code, 0)


def do_http_test(test, ep1, ep2):
    logger.info("Test {}: {} do http test {}".format(
        type(test).__name__, "="*10, "="*10))
    ep1.do_httpd()
    ep2.do_httpd()

    logger.info("Test {}: {} can curl http server on {}".format(
        type(test).__name__, ep2.ip, ep1.ip))
    exit_code = ep2.do_curl("http://{}:8000 -Ss -m 1".format(ep1.ip))[0]
    test.assertEqual(exit_code, 0)

    logger.info("Test {}: {} can curl http server on {}".format(
        type(test).__name__, ep1.ip, ep2.ip))
    exit_code = ep1.do_curl("http://{}:8000 -Ss -m 1".format(ep2.ip))[0]
    test.assertEqual(exit_code, 0)


def do_tcp_test(test, ep1, ep2):
    logger.info("Test {}: {} do tcp test {} ".format(
        type(test).__name__, "="*10, "="*10))
    ep1.do_tcp_serve()
    ep2.do_tcp_serve()

    logger.info(
        "Test {}: {} can do a tcp connection to {}".format(type(test).__name__, ep2.ip, ep1.ip))
    ep2.do_tcp_client(ep1.ip)
    exit_code = ep1.do_diff_tcp(ep2, ep1)[0]
    test.assertEqual(exit_code, 0)

    logger.info(
        "Test {}: {} can do a tcp connection to {}".format(type(test).__name__, ep1.ip, ep2.ip))
    ep1.do_tcp_client(ep2.ip)
    exit_code = ep2.do_diff_tcp(ep1, ep2)[0]
    test.assertEqual(exit_code, 0)


def do_udp_test(test, ep1, ep2):
    logger.info("Test {}: {} do udp test {} ".format(
        type(test).__name__, "="*10, "="*10))
    ep1.do_udp_serve()
    ep2.do_udp_serve()

    logger.info(
        "Test {}: {} can do a udp connection to {}".format(type(test).__name__, ep2.ip, ep1.ip))
    ep2.do_udp_client(ep1.ip)
    exit_code = ep1.do_diff_udp(ep2, ep1)[0]
    test.assertEqual(exit_code, 0)

    logger.info(
        "Test {}: {} can do a udp connection to {}".format(type(test).__name__, ep1.ip, ep2.ip))
    ep1.do_udp_client(ep2.ip)
    exit_code = ep2.do_diff_udp(ep1, ep2)[0]
    test.assertEqual(exit_code, 0)


def do_common_tests(test, ep1, ep2):
    do_ping_test(test, ep1, ep2)
    do_http_test(test, ep1, ep2)
    do_tcp_test(test, ep1, ep2)
    do_udp_test(test, ep1, ep2)


def do_long_tcp_test(test, ep1, ep2):

    logger.info("Test {}: {} do long tcp test {} ".format(
        type(test).__name__, "="*10, "="*10))
    ep1.do_tcp_serve()

    logger.info(
        "Test {}: {} can do a long tcp connection to {}, while test changes ".format(type(test).__name__, ep2.ip, ep1.ip))
    check_after = ep2.do_long_tcp_client(ep1.ip)
    test.do_scenario_change()
    sleep(check_after)
    exit_code = ep1.do_diff_tcp(ep2, ep1)[0]
    test.assertEqual(exit_code, 0)

    test.do_scenario_reset()


def do_iperf3_test(test, ep1, ep2, args=''):
    logger.info("Test {}: {} do iperf3 test with args '{}' {}".format(
        type(test).__name__, "="*10, args, "="*10))
    ep2.do_iperf3_server()

    logger.info("Test {}: {} can run perf test against server {}".format(
        type(test).__name__, ep1.ip, ep2.ip))
    exit_code = ep1.do_iperf3_client(ep2.ip, args)
    logger.info("{}".format(exit_code).replace('\\n', '\n'))
    test.assertEqual(exit_code[0], 0)

    return exit_code[1]


def do_iperf3_common_tests(test, ep1, ep2):
    ep1.host.run('mkdir -p /mnt/Transit/perflog')
    logfile = '/mnt/Transit/perflog/perf.log'

    argv = {
        '',                   # test TCP with default options
        '-P 100 -i 60',       # test TCP with 100 connections
        '-u',                 # test UDP with default options
        '-u -P 100 -i 60'     # test UDP with 100 connections
    }

    for arg in argv:
        args = '--logfile {} {}'.format(logfile, arg)
        ep1.host.run(
            '''echo 'run iperf3 with args {}' >> {}'''.format(args, logfile))
        do_iperf3_test(test, ep1, ep2, args)


def do_validate_delete_test(test, droplets):
    """
    Validates deletes RPC calls are correctly made after an update.
    * Condition #1: All update calls have a corresponding delete.
    # 2: All delete calls happen AFTER their corresponding update call is made.
    * Condition
    * Condition #3: All corresponding get RPC calls return an error after delete
    """
    exit_code = 0
    for d in droplets:
        for update in d.rpc_updates:
            if update not in d.rpc_deletes.keys():
                exit_code = 1
                logger.error(
                    "[{}]: No corresponding delete call was made for the update. {}".format(d.id, update))
                test.assertEqual(exit_code, 0)
            if d.rpc_updates[update] > d.rpc_deletes[update]:
                exit_code = 1
                logger.error(
                    "[{}]: The following update was made after delete was called. {}".format(d.id, update))
                test.assertEqual(exit_code, 0)
            if do_run_get_rpc_test(test, d, update) == 0:
                exit_code = 1
                logger.error(
                    "[{}]: Get RPC returned a valid object after delete. {}".format(d.id, update))
                test.assertEqual(exit_code, 0)
    test.assertEqual(exit_code, 0)


# Helper function for verifying delete RPC was successful
def do_run_get_rpc_test(test, droplet, call):
    if call[0] == "ep " + droplet.phy_itf or call[0] == "ep_substrate " + droplet.phy_itf:
        log_string = "[DROPLET {}]: Expecting failure for RPC call.".format(
            droplet.id)
        cmd = f'''{droplet.trn_cli_get_ep} \'{call[1]}\''''
        return droplet.exec_cli_rpc(log_string, cmd, True)[0]
    elif call[0] == "net " + droplet.phy_itf:
        log_string = "[DROPLET {}]: Expecting failure for RPC call.".format(
            droplet.id)
        cmd = f'''{droplet.trn_cli_get_net} \'{call[1]}\''''
        return droplet.exec_cli_rpc(log_string, cmd, True)[0]
    elif call[0] == "vpc " + droplet.phy_itf:
        log_string = "[DROPLET {}]: Expecting failure for RPC call.".format(
            droplet.id)
        cmd = f'''{droplet.trn_cli_get_vpc} \'{call[1]}\''''
        return droplet.exec_cli_rpc(log_string, cmd, True)[0]
    elif call[0] == "load":  # We assume agent was loaded and unloaded correctly
        return 1
    else:
        logger.error(
            "[{}]: Unidentified rpc call: {}@{}".format(droplet.id, call[0], call[1]))
        return 0


def do_check_failed_rpcs(test, droplets):
    exit_code = 0
    logger.info(
        "{} Checking for unexpected failed RPC calls {}".format('='*20, '='*20))
    for d in droplets:
        if len(d.rpc_failures.keys()) > 0:
            exit_code = 1
            for cmd in d.rpc_failures.keys():
                logger.error("[DROPLET {}]: Unexpected failed command ran: {} at {}".format(
                    d.id, d.rpc_failures[cmd], cmd))
            print()
    test.assertEqual(exit_code, 0)


def do_validate_geneve_icmp_direct_path(test, packets, droplet, pkt_ttl):
    """
    This function validates the number of geneve packets in a list of packets
    against a given count.
    """
    logger.info("{} IP: {} {}".format('='*20, droplet.ip, '='*20))
    total_geneve_icmp = sum(pkt_ttl.values())
    total_geneve_arp = 0
    for pkt in packets:
        # Checking src and dst due to docker promiscuous mode
        if GENEVE in pkt and (pkt[IP].src == droplet.ip or pkt[IP].dst == droplet.ip):
            if ICMP in pkt and pkt[IP].ttl in pkt_ttl.keys():
                pkt_ttl[pkt[IP].ttl] -= 1
            if ARP in pkt:
                total_geneve_arp += 1
    total_geneve_icmp -= sum(pkt_ttl.values())
    logger.info("{} Total geneve[ICMP]: {} {}".format(
        '*'*5, total_geneve_icmp, '*'*5))
    logger.info("{} Total geneve[ARP]: {} {}".format(
        '*'*5, total_geneve_arp, '*'*5))
    test.assertEqual(0, sum(pkt_ttl.values()))
    # If 0 geneve ICMPs, there must be 2 ARPs (switch droplet)
    if total_geneve_icmp == 0:
        test.assertEqual(total_geneve_arp, 2)


def do_validate_direct_path(test, ep1, ep2, net1_switch_host, router_host=None, net2_switch_host=None):
    """
    This function validates the functionality of the direct path.
    1. Tcpdumps to a pcap file with a timeout of 10 seconds.
    2. The common test is conducted between the two given endpoints.
    3. All geneve icmp packets are counted on each of the objects.
    4. The endpoint ICMP and switch ARP packet counts are validated against an expected count.
    5. Validate that the client has sent packets with the 4 protocol layers.
    6. Validate that the server has recieved packets with the 4 protocol layers.
    7. Validate that the switches don't recieve any packets containing the 4 tested protocol layers.
    """
    # ttl to expected pkt count maps
    exp_ep1_pkt_ttl_count = {64: 4}
    exp_ep2_pkt_ttl_count = {64: 4}
    exp_switch1_pkt_ttl_count = {0: 0}
    exp_switch2_pkt_ttl_count = {0: 0}
    exp_router_pkt_ttl_count = {0: 0}
    exp_switch_proto_count = 0
    net1_switch_host.dump_pcap_on_host(net1_switch_host.pcap_file, 10)
    ep1.host.dump_pcap_on_host(ep1.host.agent_pcap_file[ep1.veth_peer], 10)
    ep2.host.dump_pcap_on_host(ep2.host.agent_pcap_file[ep2.veth_peer], 10)
    if router_host:  # direct Path VPC case
        router_host.dump_pcap_on_host(router_host.pcap_file, 10)
        net2_switch_host.dump_pcap_on_host(net2_switch_host.pcap_file, 10)
        exp_ep1_pkt_ttl_count = {64: 2, 63: 2}
        exp_ep2_pkt_ttl_count = {64: 2, 63: 1, 61: 1}
        exp_switch1_pkt_ttl_count = {64: 1, 63: 1}
        exp_switch2_pkt_ttl_count = {62: 1, 61: 1}
        exp_router_pkt_ttl_count = {64: 3, 63: 4, 62: 1}
        exp_switch_proto_count = 1  # Switch receives first packets in router direct path case
    sleep(1)  # Wait for tcpdump to start
    do_common_tests(test, ep1, ep2)
    sleep(10)  # Wait for tcpdump to timeout

    ep1_pkts = rdpcap("test/trn_func_tests/output/" + ep1.host.ip + "_" +
                      ep1.host.agent_pcap_file[ep1.veth_peer] + "_dump.pcap")
    ep2_pkts = rdpcap("test/trn_func_tests/output/" + ep2.host.ip + "_" +
                      ep2.host.agent_pcap_file[ep2.veth_peer] + "_dump.pcap")
    net1_switch_pkts = rdpcap("test/trn_func_tests/output/" + net1_switch_host.ip + "_" +
                              net1_switch_host.pcap_file + "_dump.pcap")
    if router_host:
        router_pkts = rdpcap("test/trn_func_tests/output/" + router_host.ip + "_" +
                             router_host.pcap_file + "_dump.pcap")
        net2_switch_pkts = rdpcap("test/trn_func_tests/output/" + net2_switch_host.ip + "_" +
                                  net2_switch_host.pcap_file + "_dump.pcap")

    logger.info("{} ep1_packets {}".format('='*20, '='*20))
    # One ping is sent, endpoints sees 2 ICMPS: ICMP request, ICMP reply
    do_validate_geneve_icmp_direct_path(
        test, ep1_pkts, ep1.host, exp_ep1_pkt_ttl_count)
    logger.info("{} ep2_packets {}".format('='*20, '='*20))
    do_validate_geneve_icmp_direct_path(
        test, ep2_pkts, ep2.host, exp_ep2_pkt_ttl_count)
    logger.info("{} net1_switch_packets {}".format('='*20, '='*20))
    do_validate_geneve_icmp_direct_path(
        test, net1_switch_pkts, net1_switch_host, exp_switch1_pkt_ttl_count)

    test.assertEqual(do_check_proto(test, {ep1.host.ip: ep1_pkts}), 4)
    test.assertEqual(do_check_proto(test, {ep2.host.ip: ep2_pkts}), 4)
    test.assertEqual(do_check_proto(
        test, {net1_switch_host.ip: net1_switch_pkts}), exp_switch_proto_count)
    if router_host:
        logger.info("{} router_packets {}".format('='*20, '='*20))
        do_validate_geneve_icmp_direct_path(
            test, router_pkts, router_host, exp_router_pkt_ttl_count)
        logger.info("{} net2_switch_packets {}".format('='*20, '='*20))
        do_validate_geneve_icmp_direct_path(
            test, net2_switch_pkts, net2_switch_host, exp_switch2_pkt_ttl_count)
        test.assertEqual(do_check_proto(
            test, {router_host.ip: router_pkts}), 4)
        test.assertEqual(do_check_proto(
            test, {net2_switch_host.ip: net2_switch_pkts}), exp_switch_proto_count)


def do_start_backend_servers(test, backend):
    for ep in backend:
        ep.do_httpd()
        ep.do_tcp_serve()
        ep.do_udp_serve()


def do_start_clients(test, client, server):
    client.do_curl("http://{}:8000 -Ss -m 1".format(server.ip))[0]
    client.do_tcp_client(server.ip, detach=True)
    client.do_udp_client(server.ip, detach=True)


def do_start_pcap_scaled_ep(test, client, server, backend, timeout):
    client.host.dump_pcap_on_host(
        client.host.agent_pcap_file[client.veth_peer], timeout)
    for ep in backend:
        ep.host.dump_pcap_on_host(
            ep.host.agent_pcap_file[ep.veth_peer], timeout)
    sleep(1)  # Wait for tcpdump to start


def do_test_scaled_ep_basic(test, client, server, backend):
    """
    This function validates the functionality of the scaled endpoint.
    1. Tcpdumps to a pcap file with a timeout of 10 seconds.
    2. Test HTTP, ICMP, TCP, and UDP between client and scaled endpoint.
    3. Validate that the client has sent packets with the 4 protocol layers.
    4. Validate that the backend has recieved packets with the 4 protocol layers.
    """
    logger.info(
        "{} Testing basic scaled endpoint! {}".format('='*20, '='*20))
    do_start_pcap_scaled_ep(test, client, server, backend, 10)
    do_ping_test(test, client, server, False)
    do_start_backend_servers(test, backend)
    do_start_clients(test, client, server)
    sleep(10)  # Wait for tcpdump to timeout

    backend_packets = {}
    client_pkts = rdpcap("test/trn_func_tests/output/" + client.host.ip + "_" +
                         client.host.agent_pcap_file[client.veth_peer] + "_dump.pcap")
    for ep in backend:
        backend_packets[ep.host.ip] = (rdpcap("test/trn_func_tests/output/" + ep.host.ip + "_" +
                                              ep.host.agent_pcap_file[ep.veth_peer] + "_dump.pcap"))
    test.assertEqual(do_check_proto(test, {client.host.ip: client_pkts}), 4)
    test.assertEqual(do_check_proto(test, backend_packets), 4)


def do_test_scaled_ep_same_conn(test, client, server, backend):
    """
    This functions validates the scaled endpoint behavior when a TCP connection is kept open.
    1. Opens a TCP connection between the client endpoint and the scaled endpoint.
    2. Sends a "Hello, World!" message three times with a delay between each message.
    3. Validates that a single host in the backend recieves all three "Hello, World!" messages.
    """
    logger.info(
        "{} Testing scaled endpoint same TCP connection multiple messages! {}".format('='*20, '='*20))
    exp_pkt_count = 3
    ep_to_host_map = {}
    total_connections = 1
    do_start_pcap_scaled_ep(test, client, server, backend, 13)
    for ep in backend:
        ep.do_tcp_serve_idle(total_connections)
        ep_to_host_map[ep.host.ip] = ep.ip
    client.do_tcp_client_idle(
        server.ip, total_connections, exp_pkt_count, 5)
    sleep(15)
    backend_packets = {}
    for ep in backend:
        backend_packets[ep.host.ip] = (rdpcap("test/trn_func_tests/output/" + ep.host.ip + "_" +
                                              ep.host.agent_pcap_file[ep.veth_peer] + "_dump.pcap"))
    same_host_count = 0
    for host_ip in backend_packets.keys():
        for pkt in backend_packets[host_ip]:
            if GENEVE in pkt and TCP in pkt[GENEVE] and (pkt[IP].src == host_ip or pkt[IP].dst == host_ip):
                if Raw in pkt[GENEVE][TCP]:
                    message = pkt[GENEVE][TCP][Raw].load.decode()
                    if message == "Hello, World!" and pkt[GENEVE][IP].dst == ep_to_host_map[host_ip]:
                        same_host_count += 1
        if same_host_count == exp_pkt_count:
            break
        else:
            same_host_count = 0
    test.assertEqual(same_host_count, exp_pkt_count)


def do_test_scaled_ep_diff_conn(test, client, server, backend):
    """
    This functions validates the scaled endpoint behavior when multiple TCP connections are opened.
    1. Opens TCP connection between the client endpoint and the scaled endpoint.
    2. Sends a "Hello, World!" message on all connections.
    3. Validates that at least TWO hosts in the backend recieved the the "Hello, World!" messages.
    """
    logger.info(
        "{} Testing scaled endpoint multiple TCP connections! {}".format('='*20, '='*20))
    total_connections = 50
    ep_to_host_map = {}
    host_pkt_distrib = {}
    do_start_pcap_scaled_ep(test, client, server, backend, 10)
    for ep in backend:
        ep.do_tcp_serve_idle(total_connections)
        ep_to_host_map[ep.host.ip] = ep.ip
        host_pkt_distrib[ep.host.ip] = 0
        logger.info(
            "{} Backend Host: {} IP: {} {}".format('='*20, ep.host.id, ep.host.ip, '='*20))
    for conn in range(0, total_connections):
        client.do_tcp_client_idle(server.ip, conn)
    sleep(15)
    backend_packets = {}
    for ep in backend:
        backend_packets[ep.host.ip] = (rdpcap("test/trn_func_tests/output/" + ep.host.ip + "_" +
                                              ep.host.agent_pcap_file[ep.veth_peer] + "_dump.pcap"))
    diff_host_count = {}
    for host_ip in backend_packets.keys():
        for pkt in backend_packets[host_ip]:
            if GENEVE in pkt and TCP in pkt[GENEVE] and (pkt[IP].src == host_ip or pkt[IP].dst == host_ip):
                if Raw in pkt[GENEVE][TCP]:
                    message = pkt[GENEVE][TCP][Raw].load.decode()
                    if message == "Hello, World!" and pkt[GENEVE][IP].dst == ep_to_host_map[host_ip]:
                        diff_host_count[host_ip] = 1
                        host_pkt_distrib[host_ip] += 1
    logger.info(
        "{} {} Backend host(s) recieved a message! {}".format('='*20, sum(diff_host_count.values()), '='*20))
    for host in host_pkt_distrib.keys():
        logger.info(
            "{} Backend Host {}: recieved {} messages! {}".format('='*20, host, host_pkt_distrib[host], '='*20))
    test.assertTrue(sum(diff_host_count.values()) > 1)


def do_check_proto(test, hosts):
    """
    This function checks for protocol layers from a dictionary of packets
    """
    icmp_check = 0
    http_check = 0
    tcp_check = 0
    udp_check = 0
    for host_ip in hosts.keys():
        for pkt in hosts[host_ip]:
            if GENEVE in pkt:
                if ICMP in pkt[GENEVE] and (pkt[IP].src == host_ip or pkt[IP].dst == host_ip):
                    icmp_check = 1
                elif UDP in pkt[GENEVE] and (pkt[IP].src == host_ip or pkt[IP].dst == host_ip):
                    udp_check = 1
                elif TCP in pkt[GENEVE] and (pkt[IP].src == host_ip or pkt[IP].dst == host_ip):
                    tcp_check = 1
                    if pkt[TCP].dport == 8000 or pkt[TCP].sport == 8000:
                        http_check = 1
    return icmp_check + http_check + tcp_check + udp_check


def debug_print_icmp_packet_info(test, pkt):
    """
    Function for dumping icmp packet info for debugging purposes.
    """
    if pkt[GENEVE][ICMP].type == 0:
        icmp_type = "echo reply"
    elif pkt[GENEVE][ICMP].type == 8:
        icmp_type = "echo request"
    print("ICMP type " + icmp_type)
    print("Outer packet ttl: " + str(pkt[IP].ttl))
    print("Inner packet ttl: " + str(pkt[GENEVE][IP].ttl))
    print("Outer packet src: " + str(pkt[IP].src))
    print("Inner packet src: " + str(pkt[GENEVE][IP].src))
    print("Outer packet dst: " + str(pkt[IP].dst))
    print("Inner packet dst: " + str(pkt[GENEVE][IP].dst))
    print()


def debug_print_arp_packet_info(test, pkt):
    """
    Function for dumping arp packet info for debugging purposes.
    """
    print("ARP")
    print("Outer packet src: " + str(pkt[IP].src))
    print("Inner packet src: " + str(pkt[GENEVE][ARP].psrc))
    print("Outer packet dst: " + str(pkt[IP].dst))
    print("Inner packet dst: " + str(pkt[GENEVE][ARP].pdst))
    print()


def debug_dump_icmp_scaled_endpoint(test, client, server, backend, switch_host):
    """
    Debug scaled endpoint helper for dumping icmp packet information
    """
    client.host.dump_pcap_on_host(
        client.host.agent_pcap_file[client.veth_peer])
    switch_host.dump_pcap_on_host(switch_host.pcap_file)
    for ep in backend:
        ep.host.dump_pcap_on_host(ep.host.agent_pcap_file[ep.veth_peer])
    sleep(1)  # Wait for tcpdump to start
    do_ping_test(test, client, server, False)
    sleep(5)  # Wait for tcpdump to timeout
    backend_packets = {}
    client_pkts = rdpcap("test/trn_func_tests/output/" + client.host.ip + "_" +
                         client.host.agent_pcap_file[client.veth_peer] + "_dump.pcap")
    switch_pkts = rdpcap("test/trn_func_tests/output/" + switch_host.ip + "_" +
                         switch_host.pcap_file + "_dump.pcap")
    for ep in backend:
        backend_packets[ep.host.ip] = (rdpcap("test/trn_func_tests/output/" + ep.host.ip + "_" +
                                              ep.host.agent_pcap_file[ep.veth_peer] + "_dump.pcap"))
    logger.info("{} Client Packets: {} {}".format(
        '='*20, client.host.ip, '='*20))
    for pkt in client_pkts:
        if ICMP in pkt and (pkt[IP].src == client.host.ip or pkt[IP].dst == client.host.ip):
            debug_print_icmp_packet_info(test, pkt)
    logger.info("{} Switch Packets: {} {}".format(
        '='*20, switch_host.ip, '='*20))
    for pkt in switch_pkts:
        if ICMP in pkt and (pkt[IP].src == switch_host.ip or pkt[IP].dst == switch_host.ip):
            debug_print_icmp_packet_info(test, pkt)
    for host_ip in backend_packets.keys():
        if backend_packets[host_ip]:
            logger.info("{} Backend Packets {}: {}".format(
                '='*20, host_ip, '='*20))
        for packets in backend_packets[host_ip]:
            for pkt in packets:
                if ICMP in pkt and (pkt[IP].src == host_ip or pkt[IP].dst == host_ip):
                    debug_print_icmp_packet_info(test, pkt)

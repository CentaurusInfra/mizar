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
from scapy.all import rdpcap, IP, ARP, ICMP
from scapy.contrib.geneve import GENEVE
from time import sleep


def do_ping_test(test, ep1, ep2):
    logger.info("Test {}: {} do ping test {}".format(
        type(test).__name__, "="*10, "="*10))
    logger.info("Test: {} can ping {}".format(ep2.ip, ep1.ip))
    exit_code = ep2.do_ping(ep1.ip)[0]
    test.assertEqual(exit_code, 0)

    logger.info("Test: {} can ping {}".format(ep1.ip, ep2.ip))
    exit_code = ep1.do_ping(ep2.ip)[0]
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
    #2: All delete calls happen AFTER their corresponding update call is made.
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


def do_print_icmp_packet_info(test, pkt):
    """
    Function for dumping icmp packet info for debugging purposes.
    """
    if pkt[ICMP].type == 0:
        icmp_type = "echo reply"
    elif pkt[ICMP].type == 8:
        icmp_type = "echo request"
    print("ICMP type " + icmp_type)
    print("Outer packet ttl: " + str(pkt[IP].ttl))
    print("Inner packet ttl: " + str(pkt[GENEVE][IP].ttl))
    print("Outer packet src: " + str(pkt[IP].src))
    print("Inner packet src: " + str(pkt[GENEVE][IP].src))
    print("Outer packet dst: " + str(pkt[IP].dst))
    print("Inner packet dst: " + str(pkt[GENEVE][IP].dst))
    print()


def do_validate_geneve_icmp_fast_path(test, packets, count, droplet, exp_ttl=64):
    """
    This function validates the number of geneve packets in a list of packets
    against a given count.
    """
    logger.info("{} IP: {} {}".format('='*20, droplet.ip, '='*20))
    total_geneve_icmp = 0
    total_geneve_arp = 0
    for pkt in packets:
        # Checking src and dst due to docker promiscuous mode
        if GENEVE in pkt and (pkt[IP].src == droplet.ip or pkt[IP].dst == droplet.ip):
            if ICMP in pkt and pkt[IP].ttl == exp_ttl:
                total_geneve_icmp += 1
            if ARP in pkt:
                total_geneve_arp += 1
    logger.info("{} Total geneve[ICMP]: {} {}".format(
        '*'*5, total_geneve_icmp, '*'*5))
    logger.info("{} Total geneve[ARP]: {} {}".format(
        '*'*5, total_geneve_arp, '*'*5))
    test.assertEqual(total_geneve_icmp, count)
    # If 0 geneve ICMPs, there must be 2 ARPs (switch droplet)
    if total_geneve_icmp == 0:
        test.assertEqual(total_geneve_arp, 2)


def do_validate_fast_path(test, ep1, ep2, net1_switch_host, router_host=None, net2_switch_host=None):
    """
    This function validates the functionality of the fast path.
    1. Xdpcap dumps to a pcap file with a timeout of 5 seconds.
    2. A ping test is conducted between the two given endpoints.
    3. All geneve icmp packets are counted on each of the objects.
    4. The packet counts are validated against an expected count.
    """
    exp_ep_ttl = 64
    exp_ep_pkt_count = 4
    exp_switch_pkt_count = 0
    exp_router_pkt_count = 0

    net1_switch_host.dump_pcap(net1_switch_host.pcap_file)
    ep1.host.dump_pcap(ep1.host.agent_pcap_file[ep1.veth_peer])
    ep2.host.dump_pcap(ep2.host.agent_pcap_file[ep2.veth_peer])
    if router_host:  # Fast Path VPC case
        router_host.dump_pcap(router_host.pcap_file)
        net2_switch_host.dump_pcap(net2_switch_host.pcap_file)
        exp_ep_ttl = 63
        exp_ep_pkt_count = 2
        exp_router_pkt_count = 4
    sleep(1)  # Wait for tcpdump to start
    do_ping_test(test, ep1, ep2)
    sleep(5)  # Wait for tcpdump to timeout

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
    do_validate_geneve_icmp_fast_path(
        test, ep1_pkts, exp_ep_pkt_count, ep1.host, exp_ep_ttl)
    logger.info("{} ep2_packets {}".format('='*20, '='*20))
    do_validate_geneve_icmp_fast_path(
        test, ep2_pkts, exp_ep_pkt_count, ep2.host, exp_ep_ttl)
    logger.info("{} net1_switch_packets {}".format('='*20, '='*20))
    # One ping is sent, switch sees 0 ICMPs.
    do_validate_geneve_icmp_fast_path(
        test, net1_switch_pkts, exp_switch_pkt_count, net1_switch_host)
    if router_host:
        logger.info("{} router_packets {}".format('='*20, '='*20))
        do_validate_geneve_icmp_fast_path(
            test, router_pkts, exp_router_pkt_count, router_host)
        logger.info("{} net2_switch_packets {}".format('='*20, '='*20))
        do_validate_geneve_icmp_fast_path(
            test, net2_switch_pkts, exp_switch_pkt_count, net2_switch_host)

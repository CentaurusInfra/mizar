# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#          Haibin Michael Xie <@haibinxie>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from test.trn_controller.common import logger
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


def do_ping_fail_test(test, ep1, ep2):
    logger.info("Test {}: {} do ping FAIL test {}".format(
        type(test).__name__, "="*10, "="*10))
    logger.info("Test: {} can NOT ping {}".format(ep2.ip, ep1.ip))
    exit_code = ep2.do_ping(ep1.ip)[0]
    test.assertNotEqual(exit_code, 0)

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

    return exit_code[1];

def do_iperf3_common_tests(test, ep1, ep2):
    ep1.host.run('mkdir -p /mnt/Transit/perflog');
    logfile = '/mnt/Transit/perflog/perf.log';
    
    argv = {
        '',                   # test TCP with default options 
        '-P 100 -i 60',       # test TCP with 100 connections
        '-u',                 # test UDP with default options
        '-u -P 100 -i 60'     # test UDP with 100 connections
        }

    for arg in argv:
        args = '--logfile {} {}'.format(logfile, arg);
        ep1.host.run('''echo 'run iperf3 with args {}' >> {}'''.format(args, logfile));
        do_iperf3_test(test, ep1, ep2, args)

from common import *

def do_common_tests(test, ep1, ep2):
    do_ping_test(test, ep1, ep2)
    do_http_test(test, ep1, ep2)
    do_tcp_test(test, ep1, ep2)
    do_udp_test(test, ep1, ep2)

def do_ping_test(test, ep1, ep2, both_ways=True):
    logger.info("-------Test: PING test-------")
    logger.info("Test: {} ping {}".format(ep1.ip, ep2.ip))
    if ep1.do_ping(ep2.ip):
        logger.info("Ping test from {} to {} was Successfull".format(ep1.name, ep2.name))
    else:
        logger.info("Ping test from {} to {} FAILED".format(ep1.name, ep2.name))
    if both_ways:
        logger.info("Test: {} ping {}".format(ep2.ip, ep1.ip))
        if ep2.do_ping(ep1.ip):
            logger.info("Ping test from {} to {} was Successfull".format(ep2.name, ep1.name))
        else:
            logger.info("Ping test from {} to {} was Successfull".format(ep2.name, ep1.name))

def do_http_test(test, ep1, ep2):
    logger.info("-------Test: HTTP test-------")

    if ep2.do_curl("http://{}:8000 -Ss -m 1".format(ep1.ip)):
        logger.info("Http test from {} to {} was Successfull".format(ep2.name, ep1.name))
    else:
        logger.info("Http test from {} to {} FAILED".format(ep2.name, ep1.name))

    if ep1.do_curl("http://{}:8000 -Ss -m 1".format(ep2.ip)):
        logger.info("Http test from {} to {} was Successfull".format(ep1.name, ep2.name))
    else:
        logger.info("Http test from {} to {} FAILED".format(ep1.name, ep2.name))

def do_tcp_test(test, ep1, ep2):
    logger.info("-------Test: TCP test-------")

    if ep2.do_tcp_client(ep1.ip):
        logger.info("TCP test from {} to {} was Successfull".format(ep1.name, ep2.name))
    else:
        logger.info("TCP test from {} to {} FAILED".format(ep1.name, ep2.name))

    if ep1.do_tcp_client(ep2.ip):
        logger.info("TCP test from {} to {} was Successfull".format(ep2.name, ep1.name))
    else:
        logger.info("TCP test from {} to {} FAILED".format(ep2.name, ep1.name))

def do_udp_test(test, ep1, ep2):
    logger.info("-------Test: UDP test-------")

    if ep2.do_udp_client(ep1.ip):
        logger.info("UDP test from {} to {} was Successfull".format(ep1.name, ep2.name))
    else:
        logger.info("UDP test from {} to {} FAILED".format(ep1.name, ep2.name))

    if ep1.do_udp_client(ep2.ip):
        logger.info("UDP test from {} to {} was Successfull".format(ep2.name, ep1.name))
    else:
        logger.info("UDP test from {} to {} FAILED".format(ep2.name, ep1.name))

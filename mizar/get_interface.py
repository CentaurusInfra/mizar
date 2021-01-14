import os
import logging
logger = logging.getLogger()

def get_itf():
    default_itf = os.popen("route | grep '^default' | grep -o '[^ ]*$'").read().split('\n')[0]
    if "NET_ITF" in os.environ:
        return os.getenv("NET_ITF")
    else:
        return default_itf


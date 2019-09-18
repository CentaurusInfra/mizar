# Copyright (c) 2019 The Authors.
#
# Authors: Sherif Abdelwahab <@zasherif>
#          Phu Tran          <@phudtran>
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import logging
import subprocess
from netaddr import *

logger = logging.getLogger("transit_test")
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


class cidr:
    def __init__(self, prefixlen, ip):
        """
        Defines an IPv4 CIDR block
        """
        self.prefixlen = prefixlen
        self.ip = ip
        self.ipnet = IPNetwork("{}/{}".format(self.ip, self.prefixlen))

    def get_ip(self, idx):
        return self.ipnet[idx]

class veth_allocator:
    """
    Makes sure we create unique veth interfaces during tests
    """
    __instance = None

    @staticmethod
    def getInstance():
        if veth_allocator.__instance is None:
            veth_allocator()
        return veth_allocator.__instance

    def __init__(self):
        if veth_allocator.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            veth_allocator.__instance = self
            self.macs = []
            self.ns = []
            self.veth_peer = []

            for i in range(255):
                self.reclaim_veth("0e:73:ae:c8:87:%02x" % (i),
                                  "ns{}".format(i),
                                  "peer{}".format(i))

    def allocate_veth(self):
        return (self.macs.pop(0), self.ns.pop(0), self.veth_peer.pop(0))

    def reclaim_veth(self, mac, ns, veth_peer):
        self.macs.append(mac)
        self.ns.append(ns)
        self.veth_peer.append(veth_peer)


def run_cmd(cmd_list):
    result = subprocess.Popen(cmd_list)
    text = result.communicate()[0]
    returncode = result.returncode
    return (returncode, text)

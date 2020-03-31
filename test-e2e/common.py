
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

TEST_CLUSTER = 'kind'


def run_cmd(cmd_list):
    result = subprocess.Popen(cmd_list, shell=True, stdout=subprocess.PIPE)
    text = result.stdout.read().decode()
    returncode = result.returncode
    return (returncode, text)

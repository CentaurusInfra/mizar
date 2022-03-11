# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: The Mizar Team

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:The above copyright
# notice and this permission notice shall be included in all copies or
# substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import unittest
import logging
from mizar.common.maglev_table import MaglevTable
from mizar.tests.helper import *

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class test_basic_maglev(unittest.TestCase):

    def setUp(self):
        # The permutations table for this test
        # Element name: chain0, Permutations [1, 2, 3, 4, 5, 6, 0]
        # Element name: chain1, Permutations [4, 3, 2, 1, 0, 6, 5]
        # Element name: chain2, Permutations [5, 3, 1, 6, 4, 2, 0]

        self.table = MaglevTable(7)
        self.table.add("chain0")
        self.table.add("chain1")
        self.table.add("chain2")

    def tearDown(self):
        pass

    def test_basic_maglev(self):
        logger.info("Testing adding and removing from the maglev hash table.")

        exp_table = ["chain0", "chain0", "chain0",
                     "chain1", "chain1", "chain2", "chain2"]
        do_add_remove_maglev(self, self.table, None, None, exp_table, {})

        exp_table = ["chain1", "chain0", "chain0",
                     "chain1", "chain1", "chain0", "chain0"]
        exp_prev_ele_map = {'chain1': ['chain0'], 'chain0': ['chain2']}
        do_add_remove_maglev(self, self.table, None,
                             "chain2", exp_table, exp_prev_ele_map)

        exp_table = ["chain0", "chain0", "chain0",
                     "chain2", "chain0", "chain2", "chain2"]
        exp_prev_ele_map = {'chain0': ['chain1'],
                            'chain2': ['chain1', 'chain0']}
        do_add_remove_maglev(self, self.table, "chain2",
                             "chain1", exp_table, exp_prev_ele_map)

        exp_table = ["chain1", "chain2", "chain1",
                     "chain1", "chain1", "chain2", "chain2"]
        exp_prev_ele_map = {'chain1': [
            'chain0', 'chain2'], 'chain2': ['chain0']}
        do_add_remove_maglev(self, self.table, "chain1",
                             "chain0", exp_table, exp_prev_ele_map)

        exp_table = ["chain0", "chain0", "chain0",
                     "chain1", "chain1", "chain2", "chain2"]
        exp_prev_ele_map = {'chain0': ['chain1', 'chain2']}
        do_add_remove_maglev(self, self.table, "chain0",
                             None, exp_table, exp_prev_ele_map)

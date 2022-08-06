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

import logging

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def do_add_remove_maglev(test, table, add, remove, exp_table, exp_prev_ele_map):
    logger.info("===Add/Remove Maglev test===")
    if add:
        logger.info("Adding {} to the table.".format(add))
        table.add(add)
    if remove:
        logger.info("Removing {} from the table.".format(remove))
        table.remove(remove)
    act_table = table.get_table()
    act_prev_ele_map = table.get_prev_elements_map()
    test.assertEqual(exp_table, act_table)
    test.assertEqual(act_prev_ele_map, exp_prev_ele_map)
    logger.info("Number of elements replaced {}".format(
        table.elements_replaced))
    logger.info("Number of elements replacing {}".format(
        table.elements_replacing))

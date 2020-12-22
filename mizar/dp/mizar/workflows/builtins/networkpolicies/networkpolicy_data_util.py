# SPDX-License-Identifier: MIT
# Copyright (c) 2020 The Authors.

# Authors: Hong Chang   <@Hong-Chang>

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

def init_data_for_networkpolicy():
    data = {
        "indexed_policy_count": 0,
        "networkpolicy_map": {},
        "cidrs_map_no_except": {},
        "cidrs_map_with_except": {},
        "cidrs_map_except": {},
        "ports_map": {},
        "cidr_and_policies_map_no_except": {},
        "cidr_and_policies_map_with_except": {},
        "cidr_and_policies_map_except": {},
        "port_and_policies_map": {},
        "indexed_policy_map": {},
        "cidr_table_no_except": [],
        "cidr_table_with_except": [],
        "cidr_table_except": [],
        "port_table": [],
    }
    return data

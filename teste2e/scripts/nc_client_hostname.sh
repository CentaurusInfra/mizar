#!/bin/bash

# SPDX-License-Identifier: MIT
# Copyright (c) 2022 The Authors.

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

IP=$1
PROTOCOL=${2:-tcp}
TYPE=${3:-simple}

if [ "$PROTOCOL" == "tcp" ]
then
    if [ "$TYPE" == "scaled" ]
    then
        echo test | nc $IP 8001 -w1
    else
        echo test | nc $IP 9001 -w1
    fi
else
    if [ "$TYPE" == "scaled" ]
    then
        echo test | nc -u $IP 8002 -w1
    else
        echo test | nc -u $IP 5001 -w1
    fi
fi

#!/usr/bin/env python3

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

import socket
import sys
from time import sleep

total_conn = int(sys.argv[1])
idle = bool(int((sys.argv[2])))

if idle:
    tcp_ip = '0.0.0.0'
    tpc_port = 8000 + total_conn
    buffer_size = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, tpc_port))
    s.listen(1)
    conn, addr = s.accept()

    while 1:  # Stays open
        data = conn.recv(buffer_size)
        if data.decode() == "Hello, World!":
            print("received data: " + data.decode())
        if not data:
            break
    conn.close()
else:
    tcp_ip = '0.0.0.0'
    tpc_port = 8000
    buffer_size = 1024
    sockets = []
    for i in range(total_conn):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((tcp_ip, tpc_port + i))
        s.listen(1)
        sockets.append(s)

    for s in sockets:
        conn, addr = s.accept()
        data = conn.recv(buffer_size)
        if data.decode() == "Hello, World!":
            print("received data: " + data.decode())
        if not data:
            break
    conn.close()

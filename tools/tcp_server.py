#!/usr/bin/env python3

import socket
import sys
from time import sleep

total_conn = int(sys.argv[1])
idle = bool(int((sys.argv[2])))

if idle:
    print(idle)
    tcp_ip = '0.0.0.0'
    tpc_port = 8001
    buffer_size = 1024

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, tpc_port))
    s.listen(1)
    conn, addr = s.accept()

    while 1:  # Stays open
        data = conn.recv(buffer_size)
        print("received data:" + data.decode())
else:
    print(idle)
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
            print("received data:" + data.decode())

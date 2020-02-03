#!/usr/bin/env python3

import socket
from time import sleep
import signal
import sys

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

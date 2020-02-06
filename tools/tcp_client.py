#!/usr/bin/env python3

import socket
from time import sleep
import sys

tcp_ip = str(sys.argv[1])
message_count = int(sys.argv[2])
delay = int(sys.argv[3])
port = 8000 + int(sys.argv[4])

tpc_port = port
buffer_size = 1024
message = "Hello, World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((tcp_ip, tpc_port))
sent_messages = 0
while(sent_messages < message_count):
    s.send(message.encode())
    sent_messages += 1
    sleep(delay)
s.close()

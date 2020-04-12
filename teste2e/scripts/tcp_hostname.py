import socket

HOST = ''
PORT = 9001
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

host = bytes(socket.gethostname(), 'utf-8')

while 1:
    conn, addr = s.accept()
    while 1:
      data = conn.recv(1024)
      if not data:
        conn.sendall(b'broken')
      conn.sendall(host)
    conn.close()

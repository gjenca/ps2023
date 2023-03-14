#!/usr/bin/env python3
import socket
import sys
import os
import signal

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9999))
s.listen(5)
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
while True:

    connected_socket,client_address=s.accept()
    print('spojil sa',client_address)
    pid_child=os.fork()
    if pid_child==0:
        s.close()
        while True:
            bs=connected_socket.recv(1024)
            if not bs:
                print('koniec spojenia pre',client_address)
                break
            print('data prijate')
            connected_socket.send(b'BUMBAC '+bs)
        connected_socket.close()
        sys.exit(0)
    else:
        connected_socket.close()

#!/usr/bin/env python3
import socket
import sys
import os

server=sys.argv[1]
nick=sys.argv[2]
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
greeting_msg=f"HELLO:{nick}"
addr_server=(server,9999)
s.sendto(greeting_msg.encode("utf-8"),addr_server)
if os.fork():
    while True:
        data,addr=s.recvfrom(1024)
        if addr!=addr_server:
            continue
        msg=data.decode("utf-8").rstrip()
        if not msg.startswith("SAYS:"):
            continue
        print(msg[5:])
else:
    while True:
        line=sys.stdin.readline()
        line=line.rstrip()
        message=f"ISAY:{line}"
        s.sendto(message.encode("utf-8"),addr_server)



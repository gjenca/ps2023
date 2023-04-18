#!/usr/bin/env python3
import socket
import sys
import os
import signal
import re
import random
import email.utils

DOCUMENT_ROOT='documents'

STATUS_OK=200
STATUS_NOT_FOUND=404
STATUS_BAD_REQUEST=400
STATUS_METHOD_NOT_ALLOWED=405

STATUS_d={
    STATUS_OK:'OK',
    STATUS_NOT_FOUND:'Not found',
    STATUS_BAD_REQUEST:'Bad request',
    STATUS_METHOD_NOT_ALLOWED:'Method not allowed',
}

MIME_TYPES={
    '.html':'text/html',
    '.png':'image/png',
    '.jpg':'image/jpeg',
    '.txt':'text/plain',
}


def send_reply(f,status,headers,content):
    status_desc=STATUS_d[status]
    f.write(f'HTTP/1.1 {status} {status_desc}\r\n'.encode('ascii'))
    for key in headers:
        f.write(f'{key}: {headers[key]}\r\n'.encode('ascii'))
    f.write('\r\n'.encode('ascii'))
    f.write(content)
    f.flush()

def send_error(f,status):

    status_desc=STATUS_d[status]
    content_reply=f'<html><body><h1>{status_desc}</h1></body></html>'.encode('ascii')
    send_reply(f,status,
                {'Content-type':'text/html',
                 'Content-length':f'{len(content_reply)}'},
                 content_reply)


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
        f=connected_socket.makefile(mode='rwb')
        while True:
            first_line=f.readline().decode('ascii').rstrip()
            m=re.match('^([^ ]+) +([^ ]+) +([^ ]+)$',first_line)
            if m:
                method=m.group(1)
                url=m.group(2)
                protocol=m.group(3)
            else:
                send_error(f,STATUS_BAD_REQUEST)
                break
            print(method,url,protocol)
            if method!='GET':
                send_error(f,STATUS_METHOD_NOT_ALLOWED)
                break
            headers={}
            while True:
                header_line=f.readline().decode('ascii').rstrip()
                if not header_line:
                    break
                key,val=header_line.split(': ',1)
                headers[key.tolower()]=val
            print(headers)
            filename=DOCUMENT_ROOT+url
            try:
                with open(filename,'rb') as fr:
                    response_content=fr.read()
            except FileNotFoundError:
                send_error(f,STATUS_NOT_FOUND)
                break
            base,extension=os.path.splitext(filename)
            mtime=os.stat(filename).st_mtime
            send_reply(f,STATUS_OK,
                {'Content-type':MIME_TYPES[extension.lower()],
                 'Content-length':f'{len(response_content)}',
                 'Last-modified':email.utils.formatdate(mtime,localtime=False,usegmt=True),
                 },
                 response_content)
        f.close()
        connected_socket.close()
        sys.exit(0)
    else:
        connected_socket.close()

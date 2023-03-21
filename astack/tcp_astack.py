#!/usr/bin/env python3
import socket
import sys
import os
import signal

stack=[]

STATUS_OK=(100,'OK')
STATUS_CONTENT_EMPTY=(201,'Request content empty')
STATUS_NOT_A_NUMBER=(202,'Not a number')
STATUS_BAD_REQUEST=(301,'Bad request')
STATUS_CONTENT_NONEMPTY=(204,'Content nonempty')
STATUS_STACK_TOO_SHORT=(203,'Stack too short')
STATUS_STACK_EMPTY=(205,'Stack empty')



def read_request(f):
    """Číta požiadavku z f, vráti metódu (str) a obsah [str]
"""
    lines=[]
    while True:
        line=f.readline()
        line=line.strip()
        if not line:
            break
        lines.append(line)
    if not lines:
        return None,[]
    method=lines[0]
    content=lines[1:]
    return method,content

def method_PUSH(content):
        
        if not content:
            return STATUS_CONTENT_EMPTY,[]
        for element in content:
            if not element.isdigit():
                return STATUS_NOT_A_NUMBER,[]
        for element in content:
            stack.append(int(element))
        return STATUS_OK,[]

def method_ADD(content):
        
        if content:
            return STATUS_CONTENT_NONEMPTY,[]
        if len(stack)<2:
            return STATUS_STACK_TOO_SHORT,[]
        op1=stack.pop()
        op2=stack.pop()
        stack.append(op1+op2)
        return STATUS_OK,[]

def method_MULTIPLY(content):
        
        if content:
            return STATUS_CONTENT_NONEMPTY,[]
        if len(stack)<2:
            return STATUS_STACK_TOO_SHORT,[]
        op1=stack.pop()
        op2=stack.pop()
        stack.append(op1*op2)
        return STATUS_OK,[]

def method_PEEK(content):
        
        if content:
            return STATUS_CONTENT_NONEMPTY,[]
        if not stack:
            return STATUS_STACK_EMPTY,[]
        return STATUS_OK,[str(stack[-1])]


METHODS={
    'PUSH':method_PUSH,
    'ADD':method_ADD,
    'PEEK':method_PEEK,
    'MULTIPLY':method_MULTIPLY,
}

def handle_request(method,content):
    """Vráti status, obsah odpovede
"""
    if method in METHODS:
        return METHODS[method](content)
    else:
        return STATUS_BAD_REQUEST,[]
            
def send_response(f,status,content):

    f.write('%d %s\n' % status)
    for line in content:
        f.write('%s\n' % line)
    f.write('\n')
    f.flush()
    return


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
        f=connected_socket.makefile(mode='rw',encoding='utf-8')
        while True:
            # Precitaj poziadavku
            method,content=read_request(f)
            print(method,content)
            # Ak je method == None, treba vratit patricny status a skoncit
            if not method:
                send_response(f,STATUS_BAD_REQUEST,[])
                break
            # Vybav poziadavku
            status,reply_content=handle_request(method,content)
            # Posli odpoved
            send_response(f,status,reply_content)
            if status[0]==301:
                break
        f.close()
        connected_socket.close()
        sys.exit(0)
    else:
        connected_socket.close()

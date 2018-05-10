import socket
import select
import sys
import time
from desalgo import des
from flask import Flask, render_template, Response
from camera import VideoCamera

key = "vv_narad"
d = des()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print "Correct usage: script, IP address, port number"
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))

while True:
    sockets_list = [sys.stdin, server]
    read_sockets,write_socket, error_socket = select.select(sockets_list, [], [])
    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            msg = d.decrypt(key,message,padding = True)
            print msg
        else:
            message = sys.stdin.readline()
            msg = d.encrypt(key,message,padding = True)
            server.send(msg)
            if(message.strip() == '2'):
                fp = open('img.jpeg','wb')
                while True:
                    data = server.recv(2048)
                    if not data:
                        break
                    fp.write(data)
                fp.close()
            sys.stdout.write("<You>")
            sys.stdout.write(message)
            sys.stdout.flush()
server.close()
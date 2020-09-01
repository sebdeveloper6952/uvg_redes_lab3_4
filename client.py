#!/usr/bin/env python3

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #message ={"type":103,"idSender":-1,"idReciever":0,"message":{"id":-1,"n":1,"reciver":1,"body":""}}
    #s.sendall(repr(message).encode("utf-8"))
    message ={"type":103,"idSender":-1,"idReciever":0,"message":{"id":-1,"n":2,"reciver":1,"body":"Hola"}}
    s.sendall(repr(message).encode("utf-8"))
    s.close()
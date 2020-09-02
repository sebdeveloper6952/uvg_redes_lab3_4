#!/usr/bin/env python3

import socket
import time
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server
#A=0
#B=1
#C=2
#D=3
#E=4
#F=5
#G=6
#H=7
#I=8
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #Conect
    s.connect((HOST, PORT))
    while True:
        tm = int(input("Ingrese el tipo de mensaje (1.Crear conexion/ 2.Mandar mensaje): "))
        ids = int(input("Ingrese el sender del mensaje (id): "))
        idr = int(input("Ingrese el reciver del mensaje (id): "))
        body = input("Ingrese el cuerpo: ")
        print(tm, ids, idr, body)
        message ={"type":103,"idSender":-1,"idReciever":ids,"message":{"id":-1,"n":tm,"reciver":idr,"body":body}}
        print("Mensaje: ",message)
        s.sendall(repr(message).encode("utf-8"))
        #Send message
        #message ={"type":103,"idSender":-1,"idReciever":0,"message":{"id":-1,"n":2,"reciver":1,"body":"Hola"}}
        #message = input()
        #s.sendall(repr(message).encode("utf-8"))
        if (tm == -1):
            s.close()
            break
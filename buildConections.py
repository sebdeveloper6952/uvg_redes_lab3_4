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
    conections = [
        [1,0,1,""],
        [1,0,2,""],
        [1,0,8,""],
        [1,1,5,""],
        [1,2,3,""],
        [1,3,8,""],
        [1,3,5,""],
        [1,3,4,""],
        [1,4,6,""],
        [1,5,6,""],
        [1,5,7,""], 
    ]
    #]
    for i in conections:
        message ={"type":103,"idSender":-1,"idReciever":i[1],"message":{"id":-1,"n":i[0],"reciver":i[2],"body":i[3]}}
        s.sendall(repr(message).encode("utf-8"))
        time.sleep(1)
    s.close()
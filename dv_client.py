import socket
import sys
import json
from distance_vector import DVNode, INF
from select import select
from time import sleep

class DVClient:
    def __init__(self, host, port, node_id, neighbors):
        self.host = host
        self.port = int(port)
        self.my_id = int(node_id)
        self.node = DVNode(self.my_id, neighbors)
        print(f'Nodo {self.node.id}: mis vecinos son los nodos: {self.node.neighbors}')
        self.init_socket()
        self.run_node()

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f'Nodo {self.node.id}: conectado al servidor.')
        # enviar mensaje de login
        msg = json.dumps({"type": 101, "id": self.my_id})
        self.socket.sendall(msg.encode('utf-8'))
        data = self.socket.recv(1024)
        data = data.decode('utf-8').replace('\'', '\"')
        dec_msg = json.loads(data)
        if dec_msg['type'] == 102:
            print(f'Nodo {self.node.id}: ha iniciado sesion.')
        else:
            print(f'Nodo {self.node.id}: error al iniciar sesion.')
            exit(1)

    def run_node(self):
        while True:
            # revisar si hay mensajes por leer
            to_read, _, _ = select([self.socket], [], [], 2.0)
            
            # si hay mensajes pendientes, procesar
            if to_read:
                data = self.socket.recv(1024)
                if data:
                    print(f'Nodo {self.node.id}: hay data, leyendo...')
                    data = data.decode('utf-8')
                    print(data)
                else:
                    print(f'Nodo {self.node.id} no hay data para leer.')

            # pausa
            sleep(1 + self.node.id)

            # enviar tabla a vecinos
            for n in self.node.neighbors:
                msg = {"type": 103, "idSender": self.node.id, "idReciever": n, "message": "ola"}
                msg = json.dumps(msg)
                msg = msg.encode('utf-8')
                self.socket.sendall(msg)
                print(f'Nodo {self.node.id}: enviando mi tabla a nodo {n}, size: {len(msg)}')
                sleep(1 + self.node.id)

    def close_socket(self):
        self.socket.close()
        print(f'Nodo {self.node.id}: cerrando conexion con servidor.')
        



# creacion de este nodo
# node = DVNode(my_id, neighbors)
# print(f'Nodo {node.id}: mis vecinos son los nodos: {node.neighbors}')

# # creacion de socket y conexion a servidor
# socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# socket.connect((host, port))
# print(f'Nodo {node.id}: conectado al servidor.')

# # enviar mensaje de login
# msg = json.dumps({"type": 101, "id": my_id})
# socket.sendall(msg.encode('utf-8'))
# data = socket.recv(1024)
# data = data.decode('utf-8').replace('\'', '\"')
# dec_msg = json.loads(data)
# if dec_msg['type'] == 102:
#     print(f'Nodo {node.id}: ha iniciado sesion.')
# else:
#     print(f'Nodo {node.id}: error al iniciar sesion.')
#     exit(1)

# while True:
#     # revisar si hay mensajes por leer
#     to_read, _, _ = select([socket], [], [], 2.0)
    
#     # si hay mensajes pendientes, procesar
#     if to_read:
#         data = socket.recv(1024)
#         if data:
#             print(f'Nodo {node.id}: hay data, leyendo...')
#             data = data.decode('utf-8')
#             print(data)
#         else:
#             print(f'Nodo {node.id} no hay data para leer.')

#     # pausa
#     sleep(1 + node.id)

#     # enviar tabla a vecinos
#     for n in node.neighbors:
#         msg = {"type": 103, "idSender": node.id, "idReciever": n, "message": "ola"}
#         msg = json.dumps(msg)
#         print(f'Nodo {node.id}: enviando mi tabla a nodo {n}')
#         socket.sendall(msg.encode('utf-8'))
#         sleep(1 + node.id)


# # loop de simulacion
# # for n in node.neighbors:
# #     print(f'Nodo {node.id}: enviando mi tabla a nodo {n}')
    
# socket.close()
# print(f'Nodo {node.id}: se desconecto de servidor.')
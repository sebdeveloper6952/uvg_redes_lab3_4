import socket
import sys
import json
from distance_vector import DVNode, INF
from select import select
from time import sleep

MSG_SIZE = 2048

class DVClient:
    def __init__(self, host, port, node_id, neighbors):
        self.host = host
        self.port = int(port)
        self.my_id = int(node_id)
        self.node = DVNode(self.my_id, neighbors)
        self.init_socket()
        self.run_node()

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f'Nodo {self.node.id}: conectado al servidor.')
        # enviar mensaje de login
        msg = json.dumps({"type": 101, "id": self.my_id})
        self.socket.sendall(msg.encode('utf-8'))
        data = self.socket.recv(MSG_SIZE)
        data = data.decode('utf-8').replace('\'', '\"')
        dec_msg = json.loads(data)
        if dec_msg['type'] == 102:
            print(f'Nodo {self.node.id}: ha iniciado sesion.')
        else:
            print(f'Nodo {self.node.id}: error al iniciar sesion.')
            exit(1)

    def run_node(self):
        # enviar tabla a vecinos
        for n in self.node.neighbors:
            table_msg = {"type": 0, "table": self.node.table}
            msg = {"type": 103, "idSender": self.node.id, "idReciever": n, "message": table_msg, "p": ""}

            size = len(json.dumps(msg).encode('utf-8'))
            msg["p"] = '0' * (MSG_SIZE - size)
            
            msg = json.dumps(msg)
            msg = msg.encode('utf-8')
            self.socket.sendall(msg)
            sleep(1)
        
        iters = 0
        while True:
            # revisar si hay mensajes por leer
            to_read, _, _ = select([self.socket], [], [], 2.0)
            
            # si hay mensajes pendientes, procesar
            if to_read:
                data = self.socket.recv(MSG_SIZE)
                if len(data) == 0:
                    continue
                
                data = data.decode('utf-8').replace('\'', '\"')
                data = json.loads(data)
                if data['message']['type'] == 0:
                    if self.node.update_table(data['idSender'], data['message']['table']):
                        print(f'Nodo {self.node.id}: actualizando mi tabla...')
                        # reiniciar numero de iteraciones sin actualizaciones
                        iters = 0
                        
                        # enviar tabla a vecinos
                        for n in self.node.neighbors:
                            table_msg = {"type": 0, "table": self.node.table}
                            msg = {"type": 103, "idSender": self.node.id, "idReciever": n, "message": table_msg, "p": ""}

                            size = len(json.dumps(msg).encode('utf-8'))
                            msg["p"] = '0' * (MSG_SIZE - size)
                            
                            msg = json.dumps(msg)
                            msg = msg.encode('utf-8')
                            self.socket.sendall(msg)
                            sleep(1)
            
            iters += 1

            if iters == 10:
                print(f'Nodo {self.node.id} esta listo para enviar mensajes...')
                break
        
        # escribir tablas de cada nodo a archivo para revision
        with open(f'./output/dv_table_{self.node.id}.txt', 'w') as f:
            paths = self.node.get_shortest_paths()
            paths_s = ""
            for i in range(len(paths)):
                paths_s += 'Hacia '+str(i)+' me voy por '+str(paths[i][0])+' con costo '+str(paths[i][1])+'\n'
            f.write(paths_s)

        while True:
            print(f'Nodo {self.node.id} durmiendo...')
            sleep(1)

    def close_socket(self):
        self.socket.close()
        print(f'Nodo {self.node.id}: cerrando conexion con servidor.')
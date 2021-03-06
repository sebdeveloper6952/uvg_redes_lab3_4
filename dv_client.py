import socket
import sys
import json
from distance_vector import DVNode, INF
from select import select
from time import sleep, time
from threading import Thread
from random import randint

MSG_SIZE = 1024
LOG_FILE = './log/dv_log.txt'

class DVClient:
    def __init__(self, host, port, node_id, name, neighbors):
        self.log = ''
        self.host = host
        self.port = int(port)
        self.my_id = int(node_id)
        self.my_name = name
        self.node = DVNode(self.my_id, neighbors)

    def write_table_to_file(self):
        """
        Escribe la tabla de ruteo a un archivo de texto para revision.
        """
        print(f'Nodo {self.node.id}: escribiendo mi tabla a archivo...')
        with open(f'./output/dv_table_{self.node.id}.txt', 'w') as f:
            paths = self.node.get_shortest_paths()
            paths_s = ""
            for i in range(len(paths)):
                paths_s += 'Hacia '+str(i)+' me voy por '+str(paths[i][0])+' con costo '+str(paths[i][1])+'\n'
            f.write(paths_s)

    def write_to_log_file(self):
        """
        Escribe al archivo de log sobre los mensajes enviados a traves de este nodo.
        Tambien imprime a consola para revisión.
        """
        with open(LOG_FILE, 'a') as f:
            f.write(self.log)
        self.log = ''

    def send_table_to_neighbors(self, exceptions=[]):
        """
        Enviar tabla de ruteo de este nodo a vecinos.
        """
        print(f'Nodo {self.node.id}: enviando tabla a {self.node.neighbors}')
        for n in self.node.neighbors:
            # no enviar a estos nodos
            if n in exceptions:
                continue
            
            table_msg = {"type": 0, "table": self.node.table}
            msg = {"type": 103, "idSender": self.node.id, "idReciever": n, "message": table_msg, "p": ""}

            size = len(json.dumps(msg).encode('utf-8'))
            msg["p"] = '0' * (MSG_SIZE - size)
            
            msg = json.dumps(msg)
            msg = msg.encode('utf-8')
            self.socket.sendall(msg)
            sleep(0.25)

    def init_node(self):
        """
        Inicializacion y login.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f'Nodo {self.node.id}: conectado al servidor.')
        
        # enviar mensaje de login
        msg = json.dumps({"type": 101, "id": self.my_id, "my_id": self.my_id})
        self.socket.sendall(msg.encode('utf-8'))
        data = self.socket.recv(MSG_SIZE)
        data = data.decode('utf-8').replace('\'', '\"')
        dec_msg = json.loads(data)
        if dec_msg['type'] == 102:
            print(f'Nodo {self.node.id}: ha iniciado sesion.')
            print(f'Nodo {self.node.id}: vecinos: {self.node.neighbors}')
            self.run_node()
        else:
            print(f'Nodo {self.node.id}: error al iniciar sesion.')
            exit(1)

    def run_node(self):
        # envio inicial de tabla a vecinos
        self.send_table_to_neighbors()
        
        while True:

            # revisar si hay mensajes por leer
            to_read, _, _ = select([self.socket], [], [], 1.0)
            
            # si hay mensajes pendientes, procesar
            if to_read:
                data = self.socket.recv(MSG_SIZE)
                while len(data):
                    data = data.decode('utf-8').replace('\'', '\"')
                    data = json.loads(data)
                    node_msg = data['message']
                    msg_type = node_msg['type']

                    # Mensaje de actualización de tabla de ruteo
                    if msg_type == 0 and int(data['idReciever']) == self.node.id:
                        if self.node.update_table(data['idSender'], data['message']['table']):
                            print(f'Nodo {self.node.id}: tabla actualizada por {data["idSender"]}')
                            # enviar tabla actualizada a vecinos
                            self.send_table_to_neighbors(exceptions=[data['idSender']])

                            # imprimir tabla de este nodo a archivo
                            t = Thread(target=self.write_table_to_file)
                            t.start()
                    elif int(data['idReciever']) != self.node.id:
                        print(f'{self.node.id}: mal mensaje {data}')

                    # Mensaje de texto entre nodos
                    elif msg_type == 1:
                        self.log = ''
                        if node_msg['to'] == self.node.id:
                            # actualizar número de hops
                            node_msg['hops'] = node_msg['hops'] + 1
                            self.log += f'[{int(time())}] Nodo {self.node.id}: he recibido mensaje de texto y yo soy el destinatario final.\n'
                            self.log += f'[{int(time())}] Nodo {self.node.id}: saltos totales: {node_msg["hops"]}\n'
                            self.log += f'[{int(time())}] Nodo {self.node.id}: El mensaje es: {node_msg["msg"]}\n'
                            self.log += '******************************************************************************\n\n'
                        else:
                            # obtener siguiente nodo en ruta y su costo
                            best_id, best_cost = self.node.get_best_path_node_id(node_msg['to'])
                            
                            # revisar si nodo es quien inicia el envio de mensaje
                            if node_msg['from'] == self.node.id:
                                self.log += f'[{int(time())}] Nodo {self.node.id}: comenzaré envío de mensaje a nodo {node_msg["to"]}.\n'
                            else:
                                # actualizar número de hops
                                node_msg['hops'] = node_msg['hops'] + 1
                                self.log += f'[{int(time())}] Nodo {self.node.id}: he recibido mensaje de texto pero soy un intermediario.\n'
                                self.log += f''

                            # informacion para el archivo log
                            self.log += f'[{int(time())}] Nodo {self.node.id}: '
                            self.log += f'reenviando mensaje a {best_id} | '
                            self.log += f'distancia hacia destino final: {best_cost} | '
                            self.log += f'saltos hasta ahora: {node_msg["hops"]}\n'
                            
                            # preparar mensaje a ser reenviado
                            msg_map = {
                                "type": 103, 
                                "idSender": self.node.id,
                                "idReciever": best_id,
                                "message": node_msg, 
                                "p": ""
                            }

                            # padding
                            size = len(json.dumps(msg_map).encode('utf-8'))
                            msg_map["p"] = '0' * (MSG_SIZE - size)

                            # enviar mensaje a servidor
                            msg_json = json.dumps(msg_map)
                            msg_encoded = msg_json.encode('utf-8')
                            self.socket.sendall(msg_encoded)

                            print(f'[{int(time())}] Nodo {self.node.id}: se envió mensaje.')

                        # escribir a archivo log
                        t = Thread(target=self.write_to_log_file)
                        t.start()

                    # leer socket
                    to_read, _, _ = select([self.socket], [], [], 1.0)
                    if to_read:
                        data = self.socket.recv(MSG_SIZE)
                    else:
                        break

    def close_socket(self):
        self.socket.close()
        print(f'Nodo {self.node.id}: cerrando conexion con servidor.')
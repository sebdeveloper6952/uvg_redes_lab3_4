import socket
import sys
import json
from distance_vector import DVNode, INF
from select import select
from time import sleep, time
from threading import Thread

MSG_SIZE = 1024
LOG_FILE = './log/dv_log.txt'

class DVClient:
    def __init__(self, host, port, node_id, neighbors):
        self.log = ''
        self.host = host
        self.port = int(port)
        self.my_id = int(node_id)
        self.node = DVNode(self.my_id, neighbors)
        self.init_socket()
        sleep(1)
        self.run_node()

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
        print(self.log)
        with open(LOG_FILE, 'a') as f:
            f.write(self.log)
        self.log = ''

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
                node_msg = data['message']
                msg_type = node_msg['type']

                # Mensaje de actualización de tabla de ruteo
                if msg_type == 0:
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

                # Mensaje de texto entre nodos
                elif msg_type == 1:
                    ts = int(time())
                    self.log = ''
                    if node_msg['to'] == self.node.id:
                        self.log += f'[{ts}] Nodo {self.node.id}: he recibido mensaje de texto y yo soy el destinatario final.\n'
                        self.log += f'[{ts}] Nodo: El mensaje es: {node_msg["msg"]}\n'
                    else:
                        best_id, best_cost = self.node.get_best_path_node_id(data['message']['to'])
                        self.log += f'[{ts}] Nodo {self.node.id}: he recibido mensaje de texto pero soy un intermediario.\n'
                        self.log += f'[{ts}] Nodo: {self.node.id}: reenviando mensaje a {best_id} | distancia: {best_cost}\n'
                        
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
                        msg_json = json.dumps(msg_map).encode('utf-8')
                        self.socket.sendall(msg_json)

                    # escribir a archivo log
                    t = Thread(target=self.write_to_log_file)
                    t.start()
            
            if self.node.is_node_ready():
                print(f'Nodo {self.node.id} esta listo para enviar mensajes...')
                t = Thread(target=self.write_table_to_file)
                t.start()

            # iters += 1
            # if iters == 10:
            #     print(f'Nodo {self.node.id} esta listo para enviar mensajes...')
            #     t = Thread(target=self.write_table_to_file)
            #     t.start()

    def close_socket(self):
        self.socket.close()
        print(f'Nodo {self.node.id}: cerrando conexion con servidor.')
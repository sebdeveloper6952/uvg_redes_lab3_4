import socket
import sys
import json
from select import select
from time import sleep
from threading import Thread

LOG_FILE = './log/fl_log.txt'

class FlClient:
    def __init__(self, host, port, node_id):
        self.log = ''
        self.host = host
        self.port = int(port)
        self.my_id = int(node_id)
        self.server_id = -1
        self.init_socket()
        self.neighbors = []
        self.rMessages = []
        self.mCounter = 0
        self.run_node()
        #self.close_socket()

    def init_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        print(f'Nodo {self.my_id}: conectado al servidor.')
        self.log += f'Nodo {self.my_id}: conectado al servidor.\n'
        # enviar mensaje de login
        msg = json.dumps({"type": 101, "id": self.my_id, "my_id": self.my_id})
        self.socket.sendall(msg.encode('utf-8'))
        data = self.socket.recv(1024)
        data = data.decode('utf-8').replace('\'', '\"')
        dec_msg = json.loads(data)
        if dec_msg['type'] == 102:
            self.server_id = dec_msg['id']
            print(f'Nodo {self.my_id}: ha iniciado sesion. Server id: {self.server_id}')
            self.log += f'Nodo {self.my_id}: ha iniciado sesion. Server id: {self.server_id}\n'
        else:
            print(f'Nodo {self.my_id}: error al iniciar sesion.')
            self.log += f'Nodo {self.my_id}: error al iniciar sesion.\n'
            exit(1)
        t = Thread(target=self.write_to_log_file)
        t.start()

    def write_to_log_file(self):
        with open(LOG_FILE, 'a') as f:
            f.write(self.log)
            self.log = ''

    def run_node(self):
        while True:
            # revisar si hay mensajes por leer
            to_read, _, _ = select([self.socket], [], [], 2.0)
            # si hay mensajes pendientes, procesar
            if to_read:
                data = self.socket.recv(1024)
                if data:
                    print(f'Nodo {self.my_id}: hay data, leyendo...')
                    self.log += f'Nodo {self.my_id}: hay data, leyendo...\n'
                    data = data.decode('utf-8').replace('\'', '\"')
                    #print("Recibi: ",data)
                    for data in data.split('}{'):
                        if (data[0] != '{'):
                            data ='{' + data
                        if (data[-1] != '}'):
                            data = data +'}'
                        oS = data.count('{')
                        cS = data.count('}')
                        if (oS < cS):
                            data ='{' + data
                        if (oS > cS):
                            data = data +'}'
                        print("Antes del json", data)
                        data = json.loads(data)
                        if (data["type"] == 106): #new conexion
                            if (data["idSender"] != self.server_id):
                                self.neighbors.append(data["idSender"])
                                print('Nodo',self.my_id,': Cree una conexion con', data["idSender"])
                                self.log += f'Nodo {self.my_id} : Cree una conexion con {data["idSender"]}\n'
                        if (data["type"] == 104): #message
                            self.process_message(data["message"])
                    # escribir a archivo log
                    t = Thread(target=self.write_to_log_file)
                    t.start()

                        #pass
                    #print(data)

    def process_message(self, message): #instructions
        #data = message.decode("utf-8")
        data = message
        ## Add messages send by master
        if (data['id'] == -1): #if it is -1 , is an instruction
            print('Nodo',self.my_id,"Recibi una instruccion")
            self.log += 'Nodo {self.my_id} Recibi una instruccion\n'
            response = {}
            response["idSender"] = self.server_id
            if (data['n'] == 1): #create conection,
                response["type"] = 105
                response["idReciever"] = data['reciver']
                print('Nodo',self.my_id,"Solicitando una conexion con: ", data['reciver'])
                self.log += f'Nodo {self.my_id} Solicitando una conexion con: {data["reciver"]}\n'
                self.neighbors.append(data["reciver"])
                msg = json.dumps(response)
                msg = msg.encode('utf-8')
                self.socket.sendall(msg)
            if (data['n'] == 2): #initite message
                response["type"] = 103
                print('Nodo',self.my_id,"Creando nuevo mensaje")
                self.log += 'Nodo {self.my_id} Creando nuevo mensaje \n'
                self.rMessages.append((str( self.my_id ) + str( self.mCounter )))
                #Create the message
                body = {}
                body['id'] = self.my_id
                body['n'] = self.mCounter
                self.mCounter += 1
                body['reciver'] = data['reciver']
                body['body'] = data['body']
                response['message'] = body
                for i in self.neighbors:
                    print('Nodo',self.my_id,"Enviando mensaje a :", i)
                    response["idReciever"] = i
                    msg = json.dumps(response)
                    msg = msg.encode('utf-8')
                    self.socket.sendall(msg)
                    #time.sleep(1)
        else:
            print('Nodo',self.my_id,"Recibi un mensaje")
            self.log += 'Nodo {self.my_id} Recibi un mensaje\n'
            if (not (str( data['id'] ) + str( data['n'] )) in self.rMessages ):
                self.rMessages.append((str( data['id'] ) + str( data['n'] )))
                #check if it is for me
                if (data['reciver'] == self.my_id):
                    print('Nodo',self.my_id,"he recibido mensaje de texto y yo soy el destinatario final: Mensaje ", data['body'])
                    self.log += f'Nodo {self.my_id} he recibido mensaje de texto y yo soy el destinatario final: Mensaje {data["body"]}\n'
                else:
                    response = {}
                    response["type"] = 103
                    response["idSender"] = self.my_id
                    response["message"] = message
                    for i in self.neighbors:
                        print('Nodo',self.my_id,"he recibido mensaje de texto no soy el destinatario. Renviando a ", i)
                        self.log += f'Nodo {self.my_id} he recibido mensaje de texto no soy el destinatario. Renviando a , {i}\n'
                        response["idReciever"] = i
                        msg = json.dumps(response)
                        msg = msg.encode('utf-8')
                        self.socket.sendall(msg)
            else:
                print('Nodo',self.my_id,"Este mensaje ya se habia recibido")
                self.log += f'Nodo {self.my_id} Este mensaje ya se habia recibido\n'

                        #time.sleep(1)
    def close_socket(self):
        self.socket.close()
        print(f'Nodo {self.my_id}: cerrando conexion con servidor.')
        



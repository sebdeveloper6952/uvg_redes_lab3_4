import socket
import sys
import json
from distance_vector import DVNode, INF
from select import select
from time import sleep
import pickle 
from threading import Thread

class LsrClient:
    def __init__(self, host, port, node_id):
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
        # enviar mensaje de login
        msg = json.dumps({"type": 101, "id": self.my_id})
        self.socket.sendall(msg.encode('utf-8'))
        data = self.socket.recv(1024)
        data = data.decode('utf-8').replace('\'', '\"')
        dec_msg = json.loads(data)
        if dec_msg['type'] == 102:
            self.server_id = dec_msg['id']
            print(f'Nodo {self.my_id}: ha iniciado sesion. Server id: {self.server_id}')
        else:
            print(f'Nodo {self.my_id}: error al iniciar sesion.')
            exit(1)
    
    def run_node(self):
        i = 0
        while True:
            # revisar si hay mensajes por leer
            to_read, _, _ = select([self.socket], [], [], 2.0)
            # si hay mensajes pendientes, procesar
            if to_read:
                data = self.socket.recv(1024)
                if data:
                    print(f'Nodo {self.my_id}: hay data, leyendo...')
                    data = data.decode('utf-8').replace('\'', '\"')
                    print(data)
                    data = json.loads(data)
                    if (data["type"] == 106): #new conexion
                        if (data["idSender"] != self.server_id):
                            self.neighbors.append(data["idSender"])
                            print('Nodo',self.my_id,': Cree una conexion con', data["idSender"])
                    if (data["type"] == 104): #message
                        self.process_message(data["message"])
                        #pass
                    #print(data)

            
            while i < 1:
                #Descubrir a sus vecinos y sus direcciones
                S = set()  
                G =[]
                #Inicio de la matriz 
                for a in range(4):  
                    listo =[0, 0, 0, 0] 

                dv = DVNode(self.my_id, self.neighbors)
                    
                for b in range(4): 
                    listo[b]= int(self.my_id) #distancias
                G.append(listo) 

                source = int(self.my_id)  #Recibir origen 
                destination = int(len(self.neighbors))  #Recibir destino
                Q = [0, 1, 2, 3]
                #Medir el costo a cada uno de sus vecinos
                d =[0, 0, 0, 0]
                pi =[0, 0, 0, 0]

                #Construir el paquete con la información recabada
                for i in range(4): 
                    if(i == source): 
                        d[i]= 0
                    else: 
                        d[i]= 999
                for i in range(4): 
                    pi[i]= 9000
                S.add(source) 

                #Mientras los elementos esten en Q, se buscara la distancia minima 
                while (len(Q)!= 0):  
                    #Desde x buscar todas las minimas distancias entre los nodos 
                    x = min(d[q] for q in Q)  
                    u = 0
                    for q in Q: 
                        if(d[q]== x):   
                            u = q  #Se busca el nodo que tiene la minima distancia 
                                
                    print(u, " Es la distancia mas corta") 
                    Q.remove(u) 
                    S.add(u) 
                    adj =[] 
                    for y in range(4): 
                        if u > 0:
                            u = 0
                        if y > len(G[0]):
                            y = 0
                        if(y != u and G[u][y]!= 999):      
                            adj.append(y) #Vertice adyacente 

                    #Para cada vector adyacente se calcula la nueva distancia        
                    for v in adj:   
                        if u > len(adj):
                            u = u - 1
                        if v > len(adj):
                            v = v - 1
                        if(d[v]>(d[u]+G[u][v])): 
                            d[v]= d[u]+G[u][v]  
                            pi[v]= u

                    route =[] 
                    x = destination 

                    print("Aqui esta pI: ", pi)
                    if(pi[x]== 9000):  
                        print(source) 
                    else: 
                        while(pi[x]!= 9000):  
                            route.append(x) 
                            x = pi[x] 
                        route.reverse()  
                    #Enviar este paquete al resto
                    print('Ruta: ', route) 
                    print("Distancia desde el origen: ", pi)
                    print("Distancia de cada vector desde la fuente: ", d) 
        
    def close_socket(self):
        self.socket.close()
        print(f'Nodo {self.my_id}: cerrando conexion con servidor.')


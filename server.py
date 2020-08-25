
import selectors
import socket
import types
import json
import numpy as np

HOST = '127.0.0.1'  # localHOST
PORT = 65432        # Port
#diccionaries
users = {}
#counters
usersC = 0

def process_message(message, connection): 
    global usersC
    obj = json.loads(message)
    response =	{
        "type": 0
    }
    if (obj["type"] == 101): #101 Login
        try: 
            #Generate user id
            userId = usersC
            usersC += 1
            #Add user to list
            users[userId] =  { #id
                "id": obj["id"],
                "socket": connection
            }
            #Build response
            response["type"] = 102
            response["id"] = userId
        except:
            response["type"] = 402
    elif (obj["type"] == 103): #104 Create room
        
        #Build response
        response["type"] = 104
        response["idSender"] = obj["idSender"]
        response["idReciever"] = obj["idReciever"]
        response["message"] = obj["message"]
        #Send Message
        users[obj["idReciever"]]["socket"].send(repr(response).encode("utf-8"))
        response = None 
        
        #response["type"] = 404
    elif (obj["type"] == 105): #104 Create room
        try:
            #Build response
            response["type"] = 106
            #Send Message
            users[obj["idReciever"]]["socket"].send(repr(response).encode("utf-8"))
            users[obj["idSender"]]["socket"].send(repr(response).encode("utf-8"))
            response = None 
        except:
            response["type"] = 404
    return response

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Aceptar la conexion
    print('accepted connection from', addr)
    conn.setblocking(False)  #Eliminar llamadas bloqueadoras
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'') #Crear el objeto que va a registrar las interacciones 
    events = selectors.EVENT_READ | selectors.EVENT_WRITE #Que eventos se can a registrar
    sel.register(conn, events, data=data) # registrar los eventos de la conexion que acabamos de crear

def service_connection(key, mask):
    sock = key.fileobj #Quien mando el objeto
    data = key.data #Que objeto mando
    if mask & selectors.EVENT_READ: # Si logramos leer algo
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data: #Si leemos algo´
            data.outb += recv_data
        else: #el cliente cerro su sokcet
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE: #El socket esta listo para escribir
        if data.outb:
            #print(key, mask)
            message = data.outb
            #print("recibi", message.decode("utf-8"), type(message.decode("utf-8")))
            response = process_message(message.decode("utf-8"), sock)
            if (response):
                sock.send(repr(response).encode("utf-8"))  # Should be ready to write
                # sent = sock.send(repr(response).encode("utf-8"))  # For checking send data
            data.outb = data.outb[len(message):]
###########################################################################################

sel = selectors.DefaultSelector() #Crear el multiplexor por defecto

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Crear socket IPV4, TCP
lsock.bind((HOST, PORT)) #Amarrar la ip al puerto
lsock.listen() # Cantidad de conexiones por defecto
print('listening on', (HOST, PORT))
lsock.setblocking(False) #Eliminar llamadas bloqueadoras
sel.register(lsock, selectors.EVENT_READ, data=None) #Monitorear el socket, y registra 

while True:
    events = sel.select(timeout=None) # Esperar hasta que se registre un objeto
    for key, mask in events: #Para todos los eventos que se leyeron
        if key.data is None: # Si aun no hemos registrado el cliente
            accept_wrapper(key.fileobj) # Registrar
        else:
            service_connection(key, mask) #Procesar solicitud

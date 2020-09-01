
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

# prueba para contar numero de mensajes
msgCount = 0

def process_message(message, connection):
    global usersC
    global msgCount
    print(message)
    obj = json.loads(message)
    response =	{
        "type": 0
    }
    if (obj["type"] == 101): #101 Login
        try: 
            #Generate user id

            # experimento para sebas
            if 'my_id' in obj:
                userId = obj['my_id']
            else:
                userId = usersC
                usersC += 1

            # userId = usersC
            # usersC += 1
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
    elif (obj["type"] == 103): #104 Send message
        
        #Build response
        response["type"] = 104
        response["idSender"] = obj["idSender"]
        response["idReciever"] = obj["idReciever"]
        response["message"] = obj["message"]

        # prueba para contar numero de mensajes
        if "type" in obj["message"]:
            if obj["message"]["type"] == 0:
                msgCount += 1
                print(f'Se han enviado {msgCount} mensajes.')
        
        # incluir padding
        if "p" in obj:
            response["p"] = obj["p"]
        
        #Send Message
        users[obj["idReciever"]]["socket"].send(repr(response).encode("utf-8"))
        response = None
        
        #response["type"] = 404
    elif (obj["type"] == 105): #105 Create conexion
            #Build response
        response["type"] = 106
        response["idSender"] = obj["idSender"]
            #Send Message
        print("Objeto: ",obj)
        try:
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
            # print("recibi", message.decode("utf-8"))

            # procesar posibles múltiples mensajes
            msg_queue = message.decode('utf-8').split('}{')
            l = len(msg_queue)
            # print(f'Server: recibi {l} mensajes...')
            if l > 1:
                msg_queue[0] = msg_queue[0] = '}'
                msg_queue[-1] = '{' + msg_queue[-1]
                if l > 2:
                    for i in range(1, l - 1):
                        msg_queue[i] = '{' + msg_queue[i] + '}'
            
            for msg in msg_queue:
                # print(f'Server: procesando {msg}')
                response = process_message(message.decode('utf-8').replace('\'', '\"'), sock)
                if response:
                    sent = sock.send(repr(response).encode('utf-8'))
            data.outb = data.outb[len(message):]
            
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

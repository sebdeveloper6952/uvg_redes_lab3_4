import socket
import json
import sys

local = False
if len(sys.argv) > 1:
    local = sys.argv[1] == '1'

MSG_SIZE = 1024
LOCALHOST = '127.0.0.1'
HOST = '45.79.196.203'
PORT = 65432
h = LOCALHOST if local else HOST

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((h, PORT))
print(f'Nodo mensajero conectado al servidor.')

def print_menu():
    print(
        """
        h - Imprimir este menu.
        0 - Salir de programa.
        1 - Enviar mensaje entre nodos.
        """
    )

print_menu()
while True:
    opt = input('Ingrese opcion: ')
    if opt == '0':
        print('Terminando ejecución.')
        socket.close()
        exit(0)

    elif opt == '1':
        try:
            src = int(input('ID de nodo emisor de mensaje: '))
            dst = int(input('ID de nodo receptor de mensaje: '))
            msg = input('Ingrese el mensaje a enviar: ')
            
            node_msg = {
                "type": 1,
                "from": src,
                "to": dst,
                "msg": msg 
            }
            
            msg_map = {
                "type": 103,
                "idSender": src,
                "idReciever": src,
                "message": node_msg,
                "p": ""
            }
            
            # padding
            size = len(json.dumps(msg_map).encode('utf-8'))
            msg_map["p"] = '0' * (MSG_SIZE - size)

            # enviar mensaje a servidor
            msg_json = json.dumps(msg_map).encode('utf-8')
            socket.sendall(msg_json)

            print('El mensaje ha sido enviado al servidor.')

        
        except Exception as e:
            print(f'Error {e}.')
            continue

    elif opt == 'h':
        print_menu()

# enviar mensaje de login
# msg = json.dumps({"type": 101, "id": self.my_id})
# self.socket.sendall(msg.encode('utf-8'))
# data = self.socket.recv(MSG_SIZE)
# data = data.decode('utf-8').replace('\'', '\"')
# dec_msg = json.loads(data)
# if dec_msg['type'] == 102:
#     print(f'Nodo {self.node.id}: ha iniciado sesion.')
# else:
#     print(f'Nodo {self.node.id}: error al iniciar sesion.')
#     exit(1)
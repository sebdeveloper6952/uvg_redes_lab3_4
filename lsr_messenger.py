import socket
import json
import pickle 
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

            S = set()  
            G =[] 
                
            src = source = int(input('ID de nodo emisor de mensaje: '))
            dst = destination = int(input('ID de nodo receptor de mensaje: '))
            Q =[] 
            
            msg = input('Ingrese el mensaje a enviar: ')
            
            node_msg = {
                "type": 1,
                "from": src,
                "to": dst,
                "msg": msg,
                "hops": 0
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

            for i in range(4):  
                listo =[0, 0, 0, 0] 
                
                for j in range(4): 
                    listo[j]= int(size)
                G.append(listo) 
            
            for i in range(4): 
                Q.append(i) 
                
            d =[0, 0, 0, 0] 
            pi =[0, 0, 0, 0] 
            
            for i in range(4): 
                if(i == source): 
                    d[i]= 0
                else: 
                    d[i]= 999
            for i in range(4): 
                pi[i]= 9000
            S.add(source) 
            
            while (len(Q)!= 0):  
                
                x = min(d[q] for q in Q)  
                u = 0
                for q in Q: 
                    if(d[q]== x): 
                        u = q  
                        
                print(u, "Es la distancia mas corta") 
                Q.remove(u) # removed the minimum vertex 
                S.add(u) 
                adj =[] 
                for y in range(4): 
                    
                    # find adjacent vertices to minimum vertex 
                    if(y != u and G[u][y]!= 999):      
                        adj.append(y) 
                        
                # For each adjacent vertex, perform the update 
                # of distance and pi vectors         
                for v in adj:         
                    if(d[v]>(d[u]+G[u][v])): 
                        d[v]= d[u]+G[u][v]  
                        pi[v]= u # update adjacents distance and pi 
            route =[] 
            x = destination 
            
            # If destination is source, then pi[x]= 9000.  
            if(pi[x]== 9000):  
                print(source) 
            else: 
                
                # Find the path from destination to source 
                while(pi[x]!= 9000):  
                    route.append(x) 
                    x = pi[x] 
                route.reverse()  
                
                
            print("Ruta: ", route) # Display the route 
            print("Distancia desde el origen: ", pi) # Display the path vector 
            print("Distancia de cada vector desde la fuente:", d) # Display the distance of each node from source 

            print('El mensaje ha sido enviado al servidor.')

        
        except Exception as e:
            print(f'Error {e}.')
            continue

    elif opt == 'h':
        print_menu()
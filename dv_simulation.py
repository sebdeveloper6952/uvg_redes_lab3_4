from dv_client import DVClient
import json
from threading import Thread
import sys

local = False
if len(sys.argv) > 1:
    local = sys.argv[1] == '1'

HOST = '45.79.196.203'
LOCALHOST = '127.0.0.1'
PORT = 65432
h = LOCALHOST if local else HOST

def thread_work(id, name, neighbors):
    print(f'node {name} - id {id} - n {neighbors}')
    DVClient(h, PORT, id, name, neighbors).init_node()

threads = []
# lectura de archivo de topologia de red
with open('network.json', 'r') as file:
    json_nodes = json.loads(file.read())['nodes']
    for node in json_nodes:
        threads.append(Thread(target=thread_work, args=(node['id'], node['name'], node['neighbors'])))

for t in threads:
    t.start()

for t in threads:
    t.join()
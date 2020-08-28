from dv_client import DVClient
import json
from threading import Thread

HOST = '45.79.196.203'
PORT = 65432

def thread_work(id, neighbors):
    client = DVClient(HOST, PORT, id, neighbors)

threads = []
# lectura de archivo de topologia de red
with open('network.json', 'r') as file:
    json_nodes = json.loads(file.read())['nodes']
    for node in json_nodes:
        threads.append(Thread(target=thread_work, args=(node['id'], node['neighbors'])))

for t in threads:
    t.start()

for t in threads:
    t.join()
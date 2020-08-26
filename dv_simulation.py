from dv_client import DVClient
import json
from threading import Thread

def thread_work(id, neighbors):
    client = DVClient('127.0.0.1', 65432, id, neighbors)

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
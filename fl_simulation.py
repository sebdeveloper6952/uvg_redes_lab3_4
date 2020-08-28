from fl_client import FlClient
import json
from threading import Thread

def thread_work(id):
    client = FlClient('127.0.0.1', 65432, id)
    #print(id)

threads = []
# lectura de archivo de topologia de red
for node in range(2):
    threads.append(Thread(target=thread_work, args=(node,)))
    #print(node)

for t in threads:
    t.start()

for t in threads:
    t.join()
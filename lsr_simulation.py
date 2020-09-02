from lsr_client import LsrClient
import json
from threading import Thread
import sys

def thread_work(id):
    client = LsrClient('127.0.0.1', 65432, id)

threads = []
# lectura de archivo de topologia de red
for node in range(2):
    threads.append(Thread(target=thread_work, args=(node,)))
    #print(node)

for t in threads:
    t.start()

for t in threads:
    t.join()
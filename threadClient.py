import logging
import threading
import time

import socket

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

flag = 0

def thread_function(name):
    global flag
    while (flag != name):
        pass
    for i in range(10):
        print("Thread ", name ,": starting", i)
    time.sleep(5)
    flag += 1
    print(flag)

def write_function(name):
    a = input()
    print("El input fue", a)

if __name__ == "__main__":
    #Conect to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

    threads = list()
    for index in range(3):
        print("Main    : create and start thread ", index)
        x = threading.Thread(target=thread_function, args=(index,))
        threads.append(x)
        x.start()
    
    x = threading.Thread(target=write_function, args=(index,))
    threads.append(x)
    x.start()

    for index, thread in enumerate(threads):
        print("Main    : before joining thread ", index)
        thread.join()
        print("Main    : thread done", index)
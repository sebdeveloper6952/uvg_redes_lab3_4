import logging
import threading
import time

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
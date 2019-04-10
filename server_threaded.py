import datetime
import socket
import threading
import os
import time
import teltonikaparser
import bceparser
import esp32
import select
from pymongo import MongoClient
from pprint import pprint
import threading

from time import gmtime,strftime

fmt = "%Y-%m-%d %H:%M:%S"

TCP_IP = '192.168.168.11'
#list of ports that will be opened
TCP_PORTS = [6101,6102]
BUFFER_SIZE = 2048

# mongodb connection
myclient = MongoClient("mongodb+srv://admin:W1nd0ws87@cluster0-wkvwq.gcp.mongodb.net/test?retryWrites=true")
mydb = myclient["mydatabase"]
mycol = mydb["bce"]
raw =mydb["bceraw"]


def gen_response():
    return 'this_is_the_return_from_the_server'



def generic(data):
    print("Generic parsing task on thread: {}".format(threading.current_thread().name))
    try:
        if data:
            response=esp32.process_data(data)
            print("Server responded with - {}".format(response))
            return response
    except:
        print("Generic parsing error on thread: {}".format(threading.current_thread().name))


def bce(data):
    print("BCE parsing task on thread: {}".format(threading.current_thread().name))
    try:
        if data:
            print(data.hex())
            if data.hex()=="23424345230d0a":
                print("keyword recieved for BCE\n")
                response=None
            else:
                if data.hex() =="0d0a":
                    pass
                else:
                    raw_data = bceparser.create_dict_fromlist([data.hex()])
                    y=raw.insert_one(raw_data)
                    print("Raw Data inserted in mongodb with id {}".format(y.inserted_id))
                    value = bceparser.process_data(data.hex())
                    response = bceparser.process_ack(data.hex())
                    print("Value = {}".format(value))
                    insertdict= bceparser.create_dict_fromlist(value)
                    x=mycol.insert_one(insertdict)
                    print("Data inserted in mongodb with id {}".format(x.inserted_id))
                    print("Server responded with - {}".format(response))

            return response
    except:
        print("BCE parsing error in thread: {}".format(threading.current_thread().name))


def start_thread(connection,port,name):
    mythread = threading.Thread(target=serve_connection,args=(connection,port),name=name)

    mythread.start()

    return mythread


# creation of sockets
def create_socket(TCP_PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #dont know what below line does
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((TCP_IP,TCP_PORT))
    server_socket.listen(1)
    print("server listening on port {} on machine with ip {}".format(TCP_PORT, TCP_IP))
    return server_socket


def serve_connection(connection,port):
    try:
        print("Task assigned to thread: {}".format(threading.current_thread().name))
        while 1:
            data = connection.recv(BUFFER_SIZE)
            if not data:
                #attempt to close socket if no data
                connection.close()
                break
                exit()
            else:
                if port == 6101:
                    response=esp32.process_data(data)
                    if response:
                        print("Response to device from server")
                        print(response)
                        connection.send(response)
                elif port == 6102:
                    response=bceparser.parsed_data(data.hex())
                    if response:
                        connection.send(response)
    finally:
        connection.close()

def main():
    threadlist=[]
    print("ID of process running main program: {}".format(os.getpid()))
    open_sockets=[]

    # opening sockets based on the port list
    for i in range(0,len(TCP_PORTS)):
        open_sockets.append(create_socket(TCP_PORTS[i]))
        time.sleep(1)


    while True:
        readable, writeable, exceptional = select.select(open_sockets,[],[])
        ready_server = readable[0]


        connection, address = ready_server.accept()
        port_hit=connection.getsockname()[1]
        IP,PORT = address
        print(" Data received on socket {}".format(port_hit))
        print(" Data recieved from IP {} and port{}".format(IP,PORT))
        uid="T-"+str(IP)+"-"+str(PORT)

        threadlist.append(start_thread(connection,port_hit,uid))
                    #print "client disconnected"

    for threads in threadlist:
        threads.join()
main()





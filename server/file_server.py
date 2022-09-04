# import statements
import socket
from threading import Thread
from socketserver import ThreadingMixIn
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# setting up the IP and Port
TCP_IP = "127.0.0.1"
TCP_PORT = 60001
# buffer size
BUFFER_SIZE = 1024
# initial values of time variables 
time_end = 0
time_dict = {}
time_list = []
speed_list = []

print('TCP_IP=',TCP_IP)
print('TCP_PORT=',TCP_PORT)

# creating socket s for server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET - IPv4, SOCK_STREAM - TCP socket
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #SOL_SOCKET - protocol level, SO_REUSEADDR - allows the reuse of local address
# binding server socket with IP and Port
s.bind((TCP_IP, TCP_PORT)) #assign a local socket address to a socket

# function for recieving file
def receive_file(file_name):
    time_start = time.time()
    file_path = file_name #"server/" + file_name
    with open(file_path, 'wb') as f: #open file for writing only in binary format
        print('file opened')
        while True:
            data = client_socket.recv(1024)
            # checking condition
            if data.decode() == "close_upload":
                f.close()
                print('file close()')
                time_list.append((time.time() - time_start)*10**3)
                duration_time = (time.time() - time_start)*10**3
                print('time:  start = ', 0, ' end = ',time.time())
                print('time:  transfer_time = ', duration_time)
                return time_dict
            else:
                # writing file
                f.write(data)
                time_list.append((time.time() - time_start)*(10**3))
                if time_list[-1] == 0:
                    a = 0
                else:
                    a = (len(time_list)*(BUFFER_SIZE)) // time_list[-1]
                if not time_dict.get(time_list[-1]):
                    time_dict[time_list[-1]] = a
    

# function for sending file
def send_file(file_name):
    time_start = time.time()
    file_path = file_name #"server/" + file_name
    # file open
    with open(file_path,'rb') as f: #open file for reading only in binary format
        # while for true
        while True:
            l = f.read(BUFFER_SIZE) #read in at most 1024 bytes at once from f
            print("data", l)
            while (l):
                # sending file to client socket
                client_socket.send(l)
                time_list.append((time.time() - time_start)*(10**3))
                if time_list[-1] == 0:
                    a = 0
                else:
                    a = (len(time_list)*(BUFFER_SIZE)) // time_list[-1]
                if not time_dict.get(time_list[-1]):
                    time_dict[time_list[-1]] = a
                l = f.read(BUFFER_SIZE) 
            # when there is no data
            if not l:
                # file close
                f.close()
                time_list.append((time.time() - time_start)*10**3)
                duration_time = (time.time() - time_start)*10**3
                print('time:  start = ', 0, ' end = ',time.time())
                print('time:  transfer_time = ', duration_time)
                print("file is downloaded!!!")
                return time_dict

# function for deleting file
def delete_file(file_name):
    os.remove(file_name)

# listening client sockets
s.listen(5)
print("Waiting for incoming connections...")
(client_socket, (ip,port)) = s.accept()
print('Got connection from ', (ip,port))
while True:
    print("waiting for command from client !!!!")
    command = client_socket.recv(1024).decode()
    # checking command entered
    if command == "UPLOAD":
        file_name = client_socket.recv(1024).decode()
        print("Do you want to reveive the file '" + file_name + "' Press 'OK' to receive and 'NO' to reject")
        c = input()
        client_socket.send(c.encode("utf-8"))
        if c == "OK":
            receive_file(file_name)
        else:
            print("rejected")
    #  download command input
    elif command == "DOWNLOAD":
        file_name = client_socket.recv(1024).decode()
        present = "0"
        for (root,dirs,files) in os.walk("."): #generate the file names in a directory tree 
            for file in files:
                if file == file_name:
                    present = "1"
                    break
        client_socket.send(present.encode('utf-8')) #send file to client from server
        if present:
            send_file(file_name)
            mssg = "file found and sent"
        else:
            mssg = "no such file is found"
            print("No such file is found!!1")
        client_socket.send(mssg.encode())
    # Dir command input
    elif command == "DIR":
        files_list = ""
        for (root,dirs,files) in os.walk("."): 
            for file in files:
                files_list += file + "@"
    `    client_socket.send(files_list.encode('utf-8')) #send list of files in the server to the client
    # delete command input
    elif command == 'DELETE':
        file_name = client_socket.recv(1024).decode()
        present = 0
        for (root,dirs,files) in os.walk("."): 
            for file in files:
                if file == file_name:
                    present = 1
                    break
        if present:
            delete_file(file_name)
            # displaying appropriate messages
            print("----------- file_deleted -----------")
            mssg = "----------- file_deleted -----------"
        else:
            mssg = "----------- No such file is found -----------"
            print("\n") 
            print("----------- No such file is found -----------")
            print("\n")
        client_socket.send(mssg.encode('utf-8'))
    else:
        print("jjjjjjjjjjjjjjjjjjjjjjj")

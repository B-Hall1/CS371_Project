import socket
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# setting up the IP and Port
TCP_IP = "127.0.0.1" # Standard loopback IP address (localhost)
TCP_PORT = 60001 # Port to listen on (non-privileged ports are larger than 1023)
# buffer size
BUFFER_SIZE = 1024
# initial values of time variables 
#time_start = time.time() #0
#time_end = 0
time_dict = {} #unordered, changeable, indexed, doesn't allow duplicates, has keys and values
time_list = [] #ordered, changeable, allows duplicates

# creating socket s for client
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET - IPv4, SOCK_STREAM - TCP socket
# binding server socket with IP and Port
s.connect((TCP_IP, TCP_PORT))


# function for uploading file
def upload_file(file_name):
    time_start = time.time()
    file_path = file_name #"client/" + file_name
    with open(file_path,'rb') as f: # open file for reading only in binary format
        while True:
            l = f.read(BUFFER_SIZE) # read in at most 1024 bytes at once from f
            while (l):
                s.send(l)
                time_list.append((time.time() - time_start)*(10**3))
                # checking condition
                if time_list[-1] == 0: # last element in time_list
                    a = 0
                else:
                    a = (len(time_list)*(BUFFER_SIZE)) // time_list[-1]
                if not time_dict.get(time_list[-1]):
                    time_dict[time_list[-1]] = a
                l = f.read(BUFFER_SIZE)
            # when there is no data
            if not l:
                f.close()
                time_list.append((time.time() - time_start)*10**3)
                duration_time = (time.time() - time_start)*10**3
                print('time:  start = ', 0, ' end = ', time.time())
                print('time:  transfer_time = ', duration_time) 
                print("file uploaded and graph is shown below!!")
                return time_dict

# function for recieving file
def reveive_file(file_name):
    time_start = time.time()
    file_path = file_name #"client/" + file_name
    with open(file_path, 'wb') as f: #open file for writing only in binary format
        print('file opened')
        # while loop
        while True:
            # receiving data
            data = s.recv(1024)
            if data.decode() == "file found and sent":
                # displaying messages
                print('file close()')
                time_list.append((time.time() - time_start)*10**3)
                duration_time = (time.time() - time_start)*10**3
                print('time:  start = ', 0, ' end = ',time.time())
                print('time:  transfer_time = ', duration_time)
                break
            else:
                f.write(data)
                time_list.append((time.time() - time_start)*(10**3))
                if time_list[-1] == 0:
                    a = 0
                else:
                    a = (len(time_list)*(BUFFER_SIZE)) // time_list[-1]
                if not time_dict.get(time_list[-1]):
                    time_dict[time_list[-1]] = a
    # displaying message for graph shown
    print('file downloaded and graph is shown below!!')
    return time_dict

# function for plotting the graph
def plot_graph(time_dict):
    plt.scatter(list(time_dict.keys()), list(time_dict.values()))
    plt.ylabel('Speed in BYtes/microsecond')
    plt.xlabel('time in microseconds')
    plt.show()

# while for true condition
while True:
    # displaying instructions
    print("Use one of following commands are :: -- ")
    print("'UPLOAD' to upload a file") 
    print("'DOWNLOAD' to download a file")
    print("'DELETE' to delete a file")
    print("'DIR' to view the current directories")
    command = input()
    # if upload command is entered
    if command == "UPLOAD":
        s.send(command.encode('utf-8')) #convert entered command to hex and send to server
        print("enter the name of the file to upload")
        file_name = input()
        s.send(file_name.encode('utf-8')) #convert entered file name to hex and send to server
        response = s.recv(1024).decode() #read status sent from server in 1024 byte blocks and decode it
        if response == "OK":
            result = upload_file(file_name) 
            plot_graph(result)
            s.send("close_upload".encode("utf-8"))
        else:
            print('upload request rejected by server')
    # if download command is entered
    elif command == "DOWNLOAD":
        s.send(command.encode('utf-8'))
        print("enter the name of the file to download!!!")
        file_name = input()
        s.send(file_name.encode('utf-8'))
        present = s.recv(1024).decode()
        if present == "1":
            result = reveive_file(file_name)
            plot_graph(result)
        else:
            print("no such file is available to download!!")
    # if dir command is entered
    elif command == "DIR":
        s.send(command.encode('utf-8'))
        print("Files present in current shared folder are :: ")
        data = s.recv(1024).decode()
        data = data.split("@")
        for each in data:
            if each != "file_server.py":
                print(each)
    # if delete command is entered
    elif command == "DELETE":
        s.send(command.encode('utf-8'))
        print("Enter the name of the file to delete")
        file_name = input().encode('utf-8')
        s.send(file_name)
        mssg = s.recv(1024).decode()
        print('\n')
        print(mssg)
        print('\n')




import socket
import time
import csv
import os
import sys

# # TCP/IP setup
# host = "172.16.49.197"
# port = 5000

# get IP address and port number from command line arguments
host = sys.argv[1]
port = int(sys.argv[2])

csv_file_path = "data/"

# list files inside the csv_file_path directory
files = os.listdir(csv_file_path)
# if files exist
if files:
    # add a csv file with a consecutive number to the csv_file_path directory
    csv_file_path = csv_file_path + "data" + str(len(files)+1) + ".csv"
else:
    # add a csv file to the csv_file_path directory
    csv_file_path = csv_file_path + "data1.csv"

# create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connected = False
while not connected:
    try:
        # connect the socket to the server's address and port
        client_socket.connect((host, port))
        # check the status of the connection
        status = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        if status:
            print("TCP/IP Connection is open.")
        connected = True
    except ConnectionRefusedError:
        print("Connection refused. Retrying in 1 second...")
        time.sleep(1)


logging = True
with open(csv_file_path, mode='w') as file:
    writer = csv.writer(file)
    while logging:
        
        # send data to the server
        message = "get data"
        client_socket.sendall(message.encode('utf-8'))

        # receive data from the server
        data = client_socket.recv(1024)

        if not data:
            # server has closed the connection, break out of the loop
            break

        if data.decode('utf-8') == "ON":
                print("Logging data...")
                while True:

                    # send data to the server
                    message = "received"
                    client_socket.sendall(message.encode('utf-8'))

                    # receive data from the server
                    data = client_socket.recv(1024)

                    if not data:
                        # server has closed the connection, break out of the loop
                        break

                    if data.decode('utf-8') == "STOP":
                        logging == False
                        print("Logging stopped.")
                        break
                    else:
                        writer.writerow([data.decode('utf-8')])  # write data to CSV file

# check the status of the connection
status = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
if status == 0:
    print("Connection is closed by the server.")
else:
    print("Connection is open.")
     # close the socket
    client_socket.close()
    print("Connection to server closed")
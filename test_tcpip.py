import socket
import time
import csv
import os
import yaml



connected = False

while not connected:
    try:
        # create a TCP/IP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect the socket to the server's address and port
        client_socket.connect(("172.16.49.197", 5000))
        # check the status of the connection
        client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        connected = True
        connection_status = "TCP/IP Connection is open."
        print("TCP/IP Connection is open.")
    except ConnectionRefusedError:
        connection_status = "Connection refused. Retrying in 1 second..."
        print("Connection refused. Retrying in 1 second...")
        time.sleep(1)
    except OSError as e:
        if e.errno == 10056:
            # socket is already connected, break out of the loop
            connected = True
            connection_status = "problem on connection"
        else:
            # re-raise the exception if it's not a "already connected" error
            raise e

# reset the timeout value to None
client_socket.settimeout(None)

# send data to the server
client_socket.sendall(b"Hello, server!")

# receive data from the server
data = client_socket.recv(1024)
print("Received data:", data.decode())

# close the connection
client_socket.close()
print("TCP/IP Connection is closed.")
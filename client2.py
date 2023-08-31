import socket
import time

# TCP/IP setup
# host = "127.0.0.1"  # local machine
host = "172.16.49.197"
port = 5000

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


i = 0
while True:
    i += 1
    # send data to the server
    message = "get data"
    client_socket.sendall(message.encode('utf-8'))

    # receive data from the server
    data = client_socket.recv(1024)

    if not data:
        # server has closed the connection, break out of the loop
        break

    print("Received data:", data.decode('utf-8'))

    # send a response back to the server
    response = "Hello, server!"
    client_socket.sendall(response.encode('utf-8'))

    # wait for 50ms
    time.sleep(0.05)

    if i == 10:
        # send a message to the server to close the connection
        close_message = "quit"

        client_socket.sendall(close_message.encode('utf-8'))
         # receive data from the server
        data = client_socket.recv(1024)
        break

# receive data from the server
data = client_socket.recv(1024)
print("Received data:", data.decode('utf-8'))

# check the status of the connection
status = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
if status == 0:
    print("Connection is closed by the server.")
else:
    print("Connection is open.")
     # close the socket
    client_socket.close()
    print("Connection to server closed")



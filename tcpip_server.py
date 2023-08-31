import socket

# TCP/IP setup
host = "127.0.0.1"  # local machine
port = 5000

# create a TCP/IP socket
tcpip_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to a specific address and port
tcpip_server.bind((host, port))

# listen for incoming connections
tcpip_server.listen(1)

print("TCP/IP server started on {}:{}".format(host, port))

# wait for a connection
conn, addr = tcpip_server.accept()
print("Connected by", addr)

# receive data from the client
data = conn.recv(1024)
print("Received data:", data.decode('utf-8'))

# send a response back to the client
response = "Hello, client!"
conn.sendall(response.encode('utf-8'))

# close the connection
conn.close()
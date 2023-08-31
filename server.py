import socket
import os
import signal

# TCP/IP setup
host = "127.0.0.1"  # local machine
port = 5000

# create a TCP/IP socket
tcpip_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# bind the socket to a specific address and port
tcpip_server.bind((host, port))

# listen for incoming connections
tcpip_server.listen(20)

print("TCP/IP server started on {}:{}".format(host, port))

try:
    # wait for a connection
    conn, addr = tcpip_server.accept()
    print("Connected by", addr)

    while True:
        # receive data from the client
        data = conn.recv(1024)
        if not data:
            break
        print("Received data:", data.decode('utf-8'))

        # send a response back to the client
        response = "Hello, client!"
        conn.sendall(response.encode('utf-8'))

        # continue receiving data until a specific condition is met
        if data.decode('utf-8') == "quit":
            print("Connection to client closed")
            break

    # close the connection
    conn.close()

except KeyboardInterrupt:
    
    # close the server socket
    tcpip_server.close()
    print("Server terminated by user")
    print("Keyboard interrupt received. Exiting...")
    os.kill(os.getpid(), signal.SIGINT)
    

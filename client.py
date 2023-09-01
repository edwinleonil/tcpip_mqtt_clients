import socket
import time
import csv
import os
import yaml

# define global variables
client_socket = None
stop_logging = False
logging = False
connected = False
csv_file_path = None
host = None
port = None


# function to setup the TCP/IP connection and start logging data
def connection_setup():
    global csv_file_path
    global host
    global port
    global client_socket

    # get the IP address and port number from the config.yaml file
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    host = config["ip_address"]
    port = config["port_number"]
    
    csv_file_path = config["robot_csv_data_path"]
    # list files inside the csv_file_path directory
    files = os.listdir(csv_file_path)
    # if files exist
    if files:
        # add a csv file with a consecutive number to the csv_file_path directory
        csv_file_path = csv_file_path + "data" + str(len(files)+1) + ".csv"
    else:
        # add a csv file to the csv_file_path directory
        csv_file_path = csv_file_path + "data1.csv"


# function to setup the TCP/IP connection 
def connect_tcpip():
    # connection_setup()
    
    global logging
    global connected
    global client_socket
    global host
    global port

    connected = False
    while not connected:
        try:
            # create a TCP/IP socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect the socket to the server's address and port
            client_socket.connect((host, port))
            # check the status of the connection
            client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
            connected = True
            
            # print("TCP/IP Connection is open.")

        except ConnectionRefusedError:
            connected = False
            # print("Connection refused. Retrying in 1 second...")
            time.sleep(1)
    return connected

# function to log data
def log_data():
    global csv_file_path
    # global client_socket
    global stop_logging
    stop_logging = False
    logging = connected

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
                            stop_logging = True
                            # print("Logging stopped.")
                            break
                        else:
                            writer.writerow([data.decode('utf-8')])  # write data to CSV file
    # close the csv file
    file.close()
    close_connection()
    return stop_logging

# close the socket
def close_connection():
    global client_socket
    global connection_status
    global stop_logging

    if stop_logging == True:
        # check the status of the connection
        status = client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
        if status == 0:
            print("Connection is closed by the server.")
        else:
            print("Connection is open.")
            # close the socket
            client_socket.close()
            print("Connection to server closed")

# def main():
#     connection_setup()
#     connect_tcpip()
#     log_data()
#     close_connection()


# # run the main function
# if __name__ == "__main__":
#     main()

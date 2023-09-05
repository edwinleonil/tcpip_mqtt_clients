import socket
import sys
import time
import yaml
import csv
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal, QObject

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Client App")
        self.setGeometry(100, 100, 600, 400)
        self.config_file_path = "config.yaml"
        self.client_socket = None
        self.connected = False
        self.logging = False

        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        self.host = config["ip_address"]
        self.port = config["port_number"]
   
        self.host = str(self.host)
        self.port = int(self.port)

        self.csv_file_path = "data/"

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.ip_label = QLabel("IP Address:")
        self.ip_var = QLineEdit(str(self.host))
        self.port_label = QLabel("Port Number:")
        self.port_var = QLineEdit(str(self.port))
        self.connect_button = QPushButton("Connect")
        self.start_button = QPushButton("Start Client")
        self.stop_button = QPushButton("Stop Client")
        self.stop_button.setEnabled(False)
        self.status_label = QLabel("Status:")
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)

       
        layout = QVBoxLayout()
        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_var)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_var)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_text)
        

        self.central_widget.setLayout(layout)

        self.start_button.clicked.connect(self.logging_data)
        self.stop_button.clicked.connect(self.stop_client)
        self.connect_button.clicked.connect(self.connect_to_server)
        
        

    def connect_to_server(self):
        
        self.update_config()

        # Create a new thread to run connect_tcpip function
        self.tcpip_thread = QThread()
        # Create a new worker to run connect_tcpip function
        self.tcpip_worker = TcpipWorker(self.host, self.port, self)
        # Move the worker to the thread
        self.tcpip_worker.moveToThread(self.tcpip_thread)
        # Connect the worker's finished signal to the thread's quit method
        self.tcpip_worker.finished.connect(self.tcpip_thread.quit)
        # Connect the thread's started signal to the worker's connect_tcpip method
        self.tcpip_thread.started.connect(self.tcpip_worker.connect_tcpip)
        # Start the thread
        self.tcpip_thread.start()

    def logging_data(self):

        #start logging data thread and quit the thread when the logging is done
        self.log_thread = QThread()
        # Create a new worker to run connect_tcpip function
        self.log_worker = LogThread(self.csv_file_path, self.tcpip_worker.connected, self.tcpip_worker.client_socket, self)
        # Move the worker to the thread
        self.log_worker.moveToThread(self.log_thread)
        # Connect the worker's finished signal to the thread's quit method
        self.log_worker.finished.connect(self.log_thread.quit)
        # Connect the thread's started signal to the worker's connect_tcpip method
        self.log_thread.started.connect(self.log_worker.log_data)
        # Start the thread
        self.log_thread.start()


    def update_config(self):
        # get the IP address and port number from the config.yaml file
        with open(self.config_file_path) as f:
            config = yaml.safe_load(f)

        self.host = config["ip_address"]
        self.port = config["port_number"]
        
        self.csv_file_path = config["robot_csv_data_path"]
        # list files inside the csv_file_path directory
        files = os.listdir(self.csv_file_path)
        # if files exist
        if files:
            # add a csv file with a consecutive number to the csv_file_path directory
            self.csv_file_path = self.csv_file_path + "data" + str(len(files)+1) + ".csv"
        else:
            # add a csv file to the csv_file_path directory
            self.csv_file_path = self.csv_file_path + "data1.csv"
        # update the status text with the csv file path
        self.status_text.append("CSV file created at: " + self.csv_file_path + "\n")


    def stop_client(self):
        self.logging = False
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.connect_button.setEnabled(True)
        self.status_text.append("Client stopped\n")


class TcpipWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, host, port, App):
        super().__init__()
        self.host = str(host)
        self.port = int(port)
        self.app = App
        self.connected = False
        self.client_socket = None

        self.app.start_button.setEnabled(False)
        self.app.stop_button.setEnabled(True)
        self.app.status_text.clear()
        self.app.status_text.append("Connecting to TCP/IP server ...\n")

    def connect_tcpip(self):
        counter = 0
        while True:
            try:
                # create a TCP/IP socket
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect the socket to the server's address and port
                self.client_socket.connect((self.host, self.port))
                self.app.connect_button.setEnabled(False)
                self.app.start_button.setEnabled(True)
                self.app.stop_button.setEnabled(True)
                self.connected = True
                print("Connected to server.")
                # if connection is successful, break the loop and end the thread
                break              

            except ConnectionRefusedError:
                print("Connection refused. Retrying in 1 second...")
                time.sleep(1)
            counter += 1
            if counter == 3:
                print("Connection timed out.")
                self.app.connect_button.setEnabled(True)
                self.app.start_button.setEnabled(False)
                self.app.stop_button.setEnabled(False)
                break
        self.finished.emit()


class LogThread(QThread):
    finished = pyqtSignal()

    def __init__(self, csv_file_path, connected, client_socket, App):
        super().__init__()
        self.app = App
        self.csv_file_path = csv_file_path
        self.connected = connected
        self.client_socket = client_socket

        # disable all the buttons except the stop button
        self.app.start_button.setEnabled(False)
        self.app.connect_button.setEnabled(False)
        self.app.stop_button.setEnabled(True)

        # update the status text
        self.app.status_text.append("Logging data ...\n")

    def log_data(self):

        with open(self.csv_file_path, mode='w') as file:
            writer = csv.writer(file)

            while True:

                if self.connected == True:
                    # send data to the server
                    message = "get data"
                    self.client_socket.sendall(message.encode('utf-8'))

                    # receive data from the server
                    data = self.client_socket.recv(1024)

                    if not data:
                        # server has closed the connection, break out of the loop
                        break

                    if data.decode('utf-8') == "ON":

                            while True:

                                # send data to the server
                                message = "received"
                                self.client_socket.sendall(message.encode('utf-8'))

                                # receive data from the server
                                data = self.client_socket.recv(1024)

                                if not data:
                                    # server has closed the connection, break out of the loop
                                    break

                                if data.decode('utf-8') == "STOP":

                                    self.app.status_text.append("Logging completed.\n")
                                    self.app.stop_button.setEnabled(True)
                                    self.app.start_button.setEnabled(False)
                                    self.app.connect_button.setEnabled(False)
                                    break
                                else:
                                    writer.writerow([data.decode('utf-8')])  # write data to CSV file              
        self.finished.emit()
        self.client_socket.close()  # close the socket
        # close the csv file
        file.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())    
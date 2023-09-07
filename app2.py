import socket
import sys
import time
import yaml
import csv
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QGridLayout, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QRect


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client App")
        self.setGeometry(100, 100, 800, 400)
        
        # Center the window on the screen
        self.center()

        self.client_socket = None
        self.connected = False
        self.stop_flag = False
        self.csv_file_path = None

        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        self.host = config["ip_address"]
        self.port = config["port_number"]
        self.folder_path = config["tcpip_data_path"]
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.ip_label = QLabel("IP Address:")
        self.ip_var = QLineEdit((self.host))
        self.port_label = QLabel("Port Number:")
        self.port_var = QLineEdit(str(self.port))
        self.folder_label = QLabel("Current folder Path:")
        self.folder_var = QLineEdit(self.folder_path)
        self.folder_button = QPushButton("Change folder path")
        self.start_button = QPushButton("Connect to server and log data")
        self.stop_button = QPushButton("Stop / Stop logging and disconnect")
        self.stop_button.setEnabled(False)
        self.status_label = QLabel("Status:")
        self.status_text = QTextEdit()
        self.cursor = self.status_text.textCursor()
        self.status_text.setReadOnly(True)

        # center the text in the text box
        self.ip_var.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.port_var.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QGridLayout()

        layout.setColumnStretch(1, 2)
        layout.addWidget(self.ip_label, 0, 0)
        layout.addWidget(self.ip_var, 0, 1)
        layout.addWidget(self.port_label, 0, 2)
        layout.addWidget(self.port_var, 0, 3)
        layout.addWidget(self.folder_label, 1, 0)
        layout.addWidget(self.folder_var, 1, 1, 1, 2)
        layout.addWidget(self.folder_button, 1, 3)
        layout.addWidget(self.start_button, 2, 0, 1, 4)
        layout.addWidget(self.stop_button, 3, 0, 1, 4)
        layout.addWidget(self.status_label, 4, 0)
        layout.addWidget(self.status_text, 5, 0, 1, 4)

        self.central_widget.setLayout(layout)

        self.start_button.clicked.connect(self.logging_data)
        self.stop_button.clicked.connect(self.stop_client)
        self.folder_button.clicked.connect(self.select_folder)

    # center the window on the screen
    def center(self):
        height_offset = 100
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.frameGeometry()
        x = int(screen_geometry.center().x() - window_geometry.width() / 2)
        y = int(screen_geometry.center().y() - window_geometry.height() / 2)
        self.move(x, y-height_offset)

    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.folder_var.setText(self.folder_path)

    def logging_data(self):
        self.update_config()

        #start logging data thread and quit the thread when the logging is done
        self.log_thread = QThread()
        # Create a new worker to run connect_tcpip function
        self.log_worker = LogThread(self.csv_file_path,self.host, self.port, self)
        # Move the worker to the thread
        self.log_worker.moveToThread(self.log_thread)
        # Connect the worker's finished signal to the thread's quit method
        self.log_worker.finished.connect(self.log_thread.quit)
        # Connect the thread's started signal to the worker's connect_tcpip method
        self.log_thread.started.connect(self.log_worker.log_data)
        # Start the thread
        self.log_thread.start()


    def update_config(self):

        with open("config.yaml",'r') as f:
            config = yaml.safe_load(f)

        config["ip_address"] = self.host
        config["port_number"] = self.port
        config["robot_csv_data_path"] = self.folder_path

        with open("config.yaml",'w') as f:
            yaml.dump(config, f)

        # list files inside the csv_file_path directory
        files = os.listdir(self.folder_path)
        # if files exist
        if files:
            # add a csv file with a consecutive number to the csv_file_path directory
            self.csv_file_path = self.folder_path + "/data" + str(len(files)+1) + ".csv"
        else:
            # add a csv file to the csv_file_path directory
            self.csv_file_path = self.folder_path + "/data1.csv"
        # update the status text with the csv file path
        # self.status_text.append("CSV file created at: " + self.csv_file_path, "\n")


    def stop_client(self):
        self.stop_flag = True
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)


class LogThread(QThread):
    finished = pyqtSignal()

    def __init__(self, csv_file_path, host, port, App):

        super().__init__()

        self.app = App
        self.csv_file_path = csv_file_path

        self.host = str(host)
        self.port = int(port)

        self.connected = False
        self.client_socket = None
        self.logging_stop = False

        self.app.stop_flag = False
        self.app.start_button.setEnabled(False)
        self.app.stop_button.setEnabled(True)
        self.app.status_text.clear()
        self.on_new_message("Connecting to TCP/IP server ...\n")
        # run update_config function to update the config.yaml file
        self.app.update_config()
    
    def on_new_message(self, message):
        # Add the new message to the text box
        self.app.status_text.append(message)

        # Scroll the text box to the end
        scroll_bar = self.app.status_text.verticalScrollBar()
        max_value = scroll_bar.maximum()
        height = self.app.status_text.height()
        if max_value <= height:
            scroll_bar.setValue(height)
        else:
            scroll_bar.setValue(max_value+height)

    def connect_to_server(self):
        self.connected = False
        counter = 0
        while True:
            counter += 1

            if self.app.stop_flag == True:
                self.on_new_message("Connection attempt stopped.\n")
                self.finished.emit()
                break

            if self.logging_stop == True:
                self.client_socket.close()  # close the socket
                self.on_new_message("Logging completed")            
                self.file.close()
                self.app.start_button.setEnabled(True)
                self.app.stop_button.setEnabled(False)
                self.finished.emit()
                break

            try:
                # create a TCP/IP socket
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect the socket to the server's address and port
                self.client_socket.connect((self.host, self.port))
                self.app.start_button.setEnabled(True)
                self.app.stop_button.setEnabled(True)
                self.connected = True
                self.on_new_message("Connected to TCP/IP server")       
                break

            except ConnectionRefusedError:
                # self.on_new_message("Connection refused for {$d$}. Retrying in 1 second...\n")
                # write on the status text box the number of connection attempts
                self.on_new_message("Connection attempt: " + str(counter) +", Retrying in 1 second...")
                time.sleep(0.5)
        return self.connected

    def log_data(self):

        # run the connect_to_server function
        self.connected = self.connect_to_server()
        
        if self.connected == True:

            with open(self.csv_file_path, mode='w') as self.file:
                writer = csv.writer(self.file)
                while True:

                    if self.app.stop_flag == True:
                        self.on_new_message("Client stopped\n")
                        break
                    
                    # send data to the server
                    message = "get data"
                    self.client_socket.sendall(message.encode('utf-8'))

                    # receive data from the server
                    data = self.client_socket.recv(1024)

                    if not data:
                        self.on_new_message("No more data, server has clossed the connection")
                        
                        # server has closed the connection, break out of the loop
                        break

                    if data.decode('utf-8') == "ON":
                        self.on_new_message("Logging data...")
                        
                        while True:
                            if self.app.stop_flag == True:
                                self.on_new_message("Client stopped\n")
                                self.client_socket.close()  # close the socket
                                break

                            # send data to the server
                            message = "received"
                            self.client_socket.sendall(message.encode('utf-8'))

                            # receive data from the server
                            data = self.client_socket.recv(1024)

                            if not data:
                                self.on_new_message("No more data, server has clossed the connection\n")
                                break

                            if data.decode('utf-8') == "STOP":
                                self.logging_stop = True
                                break
                            else:
                                writer.writerow([data.decode('utf-8')])  # write data to CSV file              
            
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())    
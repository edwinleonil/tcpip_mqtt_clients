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

        self.setWindowTitle("TCP/IP and MQTT Client App")
        self.setGeometry(100, 100, 1100, 500)
        
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
        self.tcpip_folder_path = config["tcpip_data_path"]

        self.mqtt_broker_address = config["mqtt_broker_address"]
        self.mqtt_broker_port = config["mqtt_broker_port"]
        self.mqtt_topic = config["mqtt_topic"]
        self.mqtt_folder_path = config["mqtt_data_path"]
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.tcpip_client = QLabel("TCP/IP Client")
        self.mqtt_client = QLabel("MQTT Client")

        self.tcpip_label = QLabel("TCP/IP server address:")
        self.tcpip_var = QLineEdit((self.host))
        self.tcpip_port_label = QLabel("TCP/IP port Number:")
        self.tcpip_port_var = QLineEdit(str(self.port))
        self.tcpip_folder_button = QPushButton("TCP/IP data save at:")
        self.tcpip_folder_var = QLineEdit(self.tcpip_folder_path)

        self.mqtt_broker_address_label = QLabel("MQTT Broker Address:")
        self.mqtt_broker_address_var = QLineEdit(self.mqtt_broker_address)
        self.mqtt_broker_port_label = QLabel("MQTT Broker Port:")
        self.mqtt_broker_port_var = QLineEdit(str(self.mqtt_broker_port))
        self.mqtt_topic_label = QLabel("MQTT Topic:")
        self.mqtt_topic_var = QLineEdit(self.mqtt_topic)
        self.mqtt_folder_button = QPushButton("MQTT data save at:")
        self.mqtt_folder_var = QLineEdit(self.mqtt_folder_path)

        self.start_button = QPushButton("Connect to TCP/IP server and MQTT brocker and log data")
        self.stop_button = QPushButton("Stop connecting / Stop logging data and disconnect")
        self.stop_button.setEnabled(False)

        self.tcpip_status_label = QLabel("Status:")
        self.tcpip_status_text = QTextEdit()
        self.mqtt_status_label = QLabel("Status:")
        self.mqtt_status_text = QTextEdit()

        self.cursor = self.tcpip_status_text.textCursor()
        self.tcpip_status_text.setReadOnly(True)

        # center the text in the text box
        self.tcpip_client.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mqtt_client.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tcpip_var.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tcpip_port_var.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.mqtt_broker_address_var.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mqtt_broker_port_var.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QGridLayout()
        layout.setSpacing(10) # set spacing to 10 pixels

        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(3, 2)
        layout.addWidget(self.tcpip_client, 0, 0, 1, 2)
        layout.addWidget(self.mqtt_client, 0, 2, 1, 4)

        layout.addWidget(self.tcpip_label, 1, 0)
        layout.addWidget(self.tcpip_var, 1, 1)
        layout.addWidget(self.tcpip_port_label, 2, 0)
        layout.addWidget(self.tcpip_port_var, 2, 1)
        layout.addWidget(self.tcpip_folder_button, 4, 0)
        layout.addWidget(self.tcpip_folder_var, 4, 1)
        
        layout.addWidget(self.mqtt_broker_address_label, 1, 2)
        layout.addWidget(self.mqtt_broker_address_var, 1, 3)
        layout.addWidget(self.mqtt_broker_port_label, 2, 2)
        layout.addWidget(self.mqtt_broker_port_var, 2, 3)
        layout.addWidget(self.mqtt_topic_label, 3, 2)
        layout.addWidget(self.mqtt_topic_var, 3, 3)
        layout.addWidget(self.mqtt_folder_button, 4, 2)
        layout.addWidget(self.mqtt_folder_var, 4, 3)
        layout.addWidget(self.start_button, 5, 0, 1, 4)
        layout.addWidget(self.stop_button, 6, 0, 1, 4)
        layout.addWidget(self.tcpip_status_label, 7, 0)
        layout.addWidget(self.tcpip_status_text, 8, 0, 1, 2)
        layout.addWidget(self.mqtt_status_label, 7, 2)
        layout.addWidget(self.mqtt_status_text, 8, 2, 1, 4)

        self.central_widget.setLayout(layout)

        self.start_button.clicked.connect(self.logging_data)
        self.stop_button.clicked.connect(self.stop_client)
        self.tcpip_folder_button.clicked.connect(self.select_folder)

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
        self.tcpip_folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.tcpip_folder_var.setText(self.tcpip_folder_path)

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
        config["tcpip_data_path"] = self.tcpip_folder_path

        with open("config.yaml",'w') as f:
            yaml.dump(config, f)

        # list files inside the csv_file_path directory
        files = os.listdir(self.tcpip_folder_path)
        # if files exist
        if files:
            # add a csv file with a consecutive number to the csv_file_path directory
            self.csv_file_path = self.tcpip_folder_path + "/data" + str(len(files)+1) + ".csv"
        else:
            # add a csv file to the csv_file_path directory
            self.csv_file_path = self.tcpip_folder_path + "/data1.csv"


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
        self.app.tcpip_status_text.clear()
        self.on_new_message("Connecting to TCP/IP server ...\n")
        # run update_config function to update the config.yaml file
        self.app.update_config()
    
    def on_new_message(self, message):
        # Add the new message to the text box
        self.app.tcpip_status_text.append(message)

        # Scroll the text box to the end
        scroll_bar = self.app.tcpip_status_text.verticalScrollBar()
        max_value = scroll_bar.maximum()
        height = self.app.tcpip_status_text.height()
        if max_value <= height:
            scroll_bar.setValue(height)
        else:
            scroll_bar.setValue(max_value+height)
    
    def on_stop_message(self):
        self.client_socket.close()  # close the socket
        self.on_new_message("Logging completed")            
        self.file.close()
        self.app.start_button.setEnabled(True)
        self.app.stop_button.setEnabled(False)
        self.finished.emit()
        

    def connect_to_server(self):
        self.connected = False
        counter = 0
        while True:
            counter += 1

            if self.app.stop_flag == True:
                self.on_new_message("Connection attempt stopped.\n")
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
                # write on the status text box the number of connection attempts
                self.on_new_message("Connection attempt: " + str(counter) +", Retrying in 1 second...")
                time.sleep(0.5)
        return self.connected

    def log_data(self):

        # run the connect_to_server function
        self.connected = self.connect_to_server()
        
        if self.connected == True:
            self.app.stop_button.setEnabled(False)
            self.app.start_button.setEnabled(False)
            self.on_new_message("Waiting for data...\n")
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
                
                self.on_stop_message()

# add a class for the MQTT client that runs in a separate thread
class MQTTThread(QThread):
    #example 
    # def __init__(self, broker_address, broker_port, topic, filename):
    #     self.broker_address = broker_address
    #     self.broker_port = broker_port
    #     self.topic = topic
    #     self.filename = filename
    #     self.client = mqtt.Client()
    #     self.client.on_message = self.on_message
    #     self.client.connect(self.broker_address, self.broker_port, 60)
    #     self.client.subscribe(self.topic)
    #     self.client.loop_start()
    #     self.count = 1

    # def on_message(self, client, userdata, message):
    #     data = json.loads(message.payload.decode())
    #     parsed_data = data['timestamp'],data['position']['x'], data['position']['y'], data['position']['z'], data['position']['rx'], data['position']['ry'], data['position']['rz']
    #     print(parsed_data)
    #     with open(self.filename, 'a', newline='') as csvfile:
    #         writer = csv.writer(csvfile)
    #         writer.writerow(parsed_data)

    # def run(self):
    #     while self.count < 10:
    #         self.count += 1
    #         time.sleep(0.1)

    # use the previous example to create a MQTT client that runs in a separate thread

    def __init__(self, broker_address, broker_port, topic, filename):
        super().__init__()

        self.broker_address = broker_address
        self.broker_port = broker_port
        self.topic = topic
        self.filename = filename
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address, self.broker_port, 60)
        self.client.subscribe(self.topic)
        self.client.loop_start()
        self.count = 1

    def on_message(self, client, userdata, message):
        data = json.loads(message.payload.decode())
        parsed_data = data['timestamp'],data['position']['x'], data['position']['y'], data['position']['z'], data['position']['rx'], data['position']['ry'], data['position']['rz']
        print(parsed_data)
        with open(self.filename, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(parsed_data)

    def run(self):
        while self.count < 10:
            self.count += 1
            time.sleep(0.1)

            



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())    
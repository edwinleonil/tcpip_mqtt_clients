import tkinter as tk
import yaml
import socket
import time
import csv
import os


class App:
    def __init__(self, master):
        self.master = master
        master.title("Client App")
        # set the window size
        master.geometry("600x400")
        self.config_file_path = "config.yaml"
        self.client_socket = None
        self.connected = False
        self.stop_logging = False
        self.logging = False
        
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        self.host = config["ip_address"]
        self.port = config["port_number"]

        self.ip_label = tk.Label(master, text="IP Address:")
        self.ip_label.grid(row=0, column=0, padx=10, pady=10)

        self.ip_var = tk.StringVar(value=config["ip_address"])
        self.ip_entry = tk.Entry(master, textvariable=self.ip_var)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=10)

        self.port_label = tk.Label(master, text="Port Number:")
        self.port_label.grid(row=1, column=0, padx=10, pady=10)

        self.port_var = tk.StringVar(value=config["port_number"])
        self.port_entry = tk.Entry(master, textvariable=self.port_var)
        self.port_entry.grid(row=1, column=1, padx=10, pady=10)

        self.start_button = tk.Button(master, text="Start Client", command=self.start_client)
        self.start_button.grid(row=2, column=0, padx=10, pady=10)

        self.stop_button = tk.Button(master, text="Stop Client", command=self.stop_client, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=1, padx=10, pady=10)

        self.status_label = tk.Label(master, text="Status:")
        self.status_label.grid(row=3, column=0, padx=10, pady=10)

        self.status_text = tk.Text(master, height=10, width=50)
        self.status_text.grid(row=3, column=1, padx=10, pady=10)

    def connection_setup(self):

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
        
        # return self.host, self.port, self.csv_file_path

    def start_client(self):
        self.client_socket = None
        self.connected = False
        self.stop_logging = False
        self.logging = False

        self.ip_address = self.ip_entry.get() or self.ip_var
        self.port_number = self.port_entry.get() or self.port_var 
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.status_text.delete('1.0', tk.END)

        self.status_text.insert(tk.END, "Client started\n")
        self.status_text.update_idletasks()  # update widget immediately
        self.status_text.after(1, self.update_status)
        
        self.update_config()
        self.connection_setup()
        
        connected =  self.connect_tcpip()
        
        if connected:
            self.log_data()
        else:
            self.status_text.insert(tk.END, "Connection failed\n")
            self.status_text.update_idletasks()


    # function to setup the TCP/IP connection 
    def connect_tcpip(self):

        while not self.connected:
            try:
                # create a TCP/IP socket
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # connect the socket to the server's address and port
                self.client_socket.connect((self.host, self.port))
                # check the status of the connection
                self.client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
                self.connected = True
                self.status_text.delete('1.0', tk.END)
                self.status_text.insert(tk.END, "TCP/IP Connection is open.\n")
                self.status_text.update_idletasks()  # update widget immediately
                # self.status_text.after(1, self.update_status)

            except ConnectionRefusedError:
                self.connected = False
                # print("Connection refused. Retrying in 1 second...")
                self.status_text.insert(tk.END, "Connection refused. Retrying in 1 second...\n")
                print("Connection refused. Retrying in 1 second...")
                self.status_text.update_idletasks()  # update widget immediately
                # self.status_text.after(1, self.update_status)     
                time.sleep(1)           
                
            # exit the loop if the stop button is pressed
            if self.stop_button["state"] == tk.DISABLED:
                break
          
        return self.connected

    def log_data(self):
        
        # client_socket = self.client_socket
        self.csv_file_path = self.csv_file_path
        self.logging = self.connected 

        with open(self.csv_file_path, mode='w') as file:
            writer = csv.writer(file)
            while self.logging:
                
                # send data to the server
                message = "get data"
                self.client_socket.sendall(message.encode('utf-8'))

                # receive data from the server
                data = self.client_socket.recv(1024)

                if not data:
                    # server has closed the connection, break out of the loop
                    break

                if data.decode('utf-8') == "ON":
                        self.status_text.insert(tk.END, "Logging data ...\n")
                        self.status_text.update_idletasks()  # update widget immediately
                        self.status_text.after(1, self.update_status)
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
                                self.logging == False
                                self.stop_logging = True
                                self.status_text.insert(tk.END, "Logging data completed\n")
                                self.status_text.update_idletasks()  # update widget immediately
                                self.status_text.after(1, self.update_status)
                                break
                            else:
                                writer.writerow([data.decode('utf-8')])  # write data to CSV file              
        # close the csv file
        file.close()
        return

    def update_status(self):
        # Update the widget and schedule another update
        self.status_text.update_idletasks()
        self.status_text.after(1, self.update_status)

    def update_config(self):

        with open("config.yaml",'r') as f:
            config = yaml.safe_load(f)

        config["ip_address"] = str(self.ip_address)
        config["port_number"] = int(self.port_number)

        with open("config.yaml",'w') as f:
            yaml.dump(config, f)

    def stop_client(self):
        
        # self.process.terminate()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_text.insert(tk.END, "Client stopped\n")
        self.status_text.update_idletasks()  # update widget immediately
        self.status_text.after(1, self.update_status)
        
        if self.stop_logging:
            print("Connection was closed by the server.")
        # check if the client is connected to the server
        if self.connected:
            # close the socket
            self.client_socket.close()
            print("Connection to server closed by client.")

        

root = tk.Tk()
app = App(root)
root.mainloop()
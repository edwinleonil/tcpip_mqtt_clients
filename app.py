import tkinter as tk
import subprocess
import yaml

class App:
    def __init__(self, master):
        self.master = master
        master.title("Client App")

        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

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

        self.status_text = tk.Text(master, height=5, width=30)
        self.status_text.grid(row=3, column=1, padx=10, pady=10)

    def start_client(self):
        ip_address = self.ip_entry.get() or self.ip_var
        port_number = self.port_entry.get() or self.port_var 
        self.process = subprocess.Popen(["python", "client.py", ip_address, port_number])
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, "Client started\n")

        with open("config.yaml", "w") as f:
            yaml.dump({"ip_address": ip_address, "port_number": port_number}, f)

    def stop_client(self):
        self.process.terminate()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_text.insert(tk.END, "Client stopped\n")

root = tk.Tk()
app = App(root)
root.mainloop()
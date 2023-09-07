import paho.mqtt.client as mqtt
import json
import time
import csv

class App:
    def __init__(self, broker_address, broker_port, topic, filename):
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

app = App(broker_address = "192.168.131.214", broker_port=1883, topic="ORA/v1/instrument/measurements/Static.Constellation->Spindle.SMR", filename="data/mqtt_data.csv")
app.run()
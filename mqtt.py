import paho.mqtt.client as mqtt
import time
import json

# Define the MQTT broker address and port
broker_address = "192.168.131.214"
broker_port = 1883

# Define the MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(broker_address, broker_port)

# Start the MQTT client loop
client.loop_start()

# Subscribe to the topic
client.subscribe("ORA/v1/instrument/measurements/Static.Constellation->Spindle.SMR")
count = 1
if count == 0:
    # read and print the message payload from the topic every time a message is published
    def on_message(client, userdata, message):
        data = json.loads(message.payload.decode())
        parsed_data = data['position']['x'], data['position']['y'], data['position']['z'], data['position']['rx'], data['position']['ry'], data['position']['rz']

        print(parsed_data)

    client.on_message = on_message

    # Wait for messages
    while count < 10:
        count += 1
        time.sleep(0.1)

    # Stop the MQTT client loop
    client.loop_stop()


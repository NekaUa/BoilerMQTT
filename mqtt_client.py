import configparser
from time import sleep

import Boiler
from paho.mqtt import client as mqtt_client


class MQTT_Client:
    def __init__(self, boiler, client_id=f'Boiler'):
        self.config = configparser.ConfigParser()  # создаём объекта парсера
        self.config.read("settings.ini")  # читаем конфиг
        self.client_id = client_id
        self.broker = self.config["MQTT"]["broker"]
        self.port = int(self.config["MQTT"]["port"])
        self.topicTemp = self.config["MQTT"]["topicTemp"]
        self.topicTargetTemp = self.config["MQTT"]["topicTargetTemp"]
        self.topicState = self.config["MQTT"]["topicState"]
        self.topicAnibacterial = self.config["MQTT"]["topicAnibacterial"]
        self.subTopicTargetTemp = self.config["MQTT"]["subTopicTargetTemp"]
        self.subTopicState = self.config["MQTT"]["subTopicState"]
        self.subTopicAnibacterial = self.config["MQTT"]["subTopicAnibacterial"]
        self.subTopicRefresh = self.config["MQTT"]["subTopicRefresh"]
        self.client = mqtt_client.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.username = self.config["MQTT"]["username"]
        self.password = self.config["MQTT"]["password"]
        self.connect()
        self.boiler = boiler
        self.publish(self.boiler)
        self.subscribe()


    def connect(self):
        self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.broker, self.port)

    def disconnect(self):
        self.client.disconnect()

    def publish(self, boiler: Boiler.Boiler):
        attempts = 100 # Number of attempts to send data
        while True:
            answer = self.client.publish(self.topicTemp, boiler.temperature) # Send temperature
            if answer[0] != 0: # If error
                print("Failed to send message to topic Temp") # Print error message
                attempts -= 1 # Decrement attempts
                sleep(1) # Wait 1 second
            else: # If no error
                break # Exit loop
            if attempts == 0: # If attempts == 0
                break # Exit loop
        attempts = 100
        while True:
            answer = self.client.publish(self.topicTargetTemp, boiler.targetTemperature)
            if answer[0] != 0:
                print("Failed to send message to topic TargetTemp")
                attempts -= 1
                sleep(1)
            else:
                break
            if attempts == 0:
                break
        attempts = 100
        while True:
            if boiler.state == Boiler.BoilerState.OFF:
                state = "Power Off"
            elif boiler.state == Boiler.BoilerState.POWER_1:
                state = "Power 1"
            elif boiler.state == Boiler.BoilerState.POWER_2:
                state = "Power 2"
            elif boiler.state == Boiler.BoilerState.POWER_3:
                state = "Power 3"
            elif boiler.state == Boiler.BoilerState.POWER_TIMER:
                state = "Timer"
            elif boiler.state == Boiler.BoilerState.POWER_NOFROST:
                state = "No Frost"
            else:
                state = "Power Off"
            answer = self.client.publish(self.topicState, state)
            if answer[0] != 0:
                print("Failed to send message to topic State")
                attempts -= 1
                sleep(1)
            else:
                break
            if attempts == 0:
                break
        attempts = 100
        while True:
            answer = self.client.publish(self.topicAnibacterial, boiler.antibacterial)
            if answer[0] != 0:
                print("Failed to send message to topic Anibacterial")
                attempts -= 1
                sleep(1)
            else:
                break
            if attempts == 0:
                break
        print("Published: " + str(boiler.temperature) + " C, " + str(boiler.targetTemperature) + " C, " + str(boiler.state) + ", " + str(boiler.antibacterial))


    def subscribe(self):
        self.client.subscribe(self.subTopicAnibacterial)
        self.client.subscribe(self.subTopicState)
        self.client.subscribe(self.subTopicTargetTemp)
        self.client.subscribe(self.subTopicRefresh)


    def run(self):
        self.client.loop_forever()
        # self.client.loop_start()

    def stop(self):
        self.client.loop_stop()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected MQTT disconnection. Will auto-reconnect")

    def on_message(self, client, userdata, msg):
        if msg.topic != self.subTopicRefresh:
            if msg.topic == self.subTopicTargetTemp:
                self.boiler.targetTemperature = int(msg.payload.decode())
            elif msg.topic == self.subTopicState:
                if(msg.payload.decode() == "Power Off"):
                    self.boiler.state = Boiler.BoilerState.OFF
                elif(msg.payload.decode() == "Power 1"):
                    self.boiler.state = Boiler.BoilerState.POWER_1
                elif(msg.payload.decode() == "Power 2"):
                    self.boiler.state = Boiler.BoilerState.POWER_2
                elif(msg.payload.decode() == "Power 3"):
                    self.boiler.state = Boiler.BoilerState.POWER_3
                elif(msg.payload.decode() == "Timer"):
                    self.boiler.state = Boiler.BoilerState.POWER_TIMER
                elif msg.payload.decode() == "No Frost":
                    self.boiler.state = Boiler.BoilerState.POWER_NOFROST
            elif msg.topic == self.subTopicAnibacterial:
                self.boiler.antibacterial = int(msg.payload.decode())
            self.boiler.set_state()  # Set state of boiler
            self.boiler.get_state()  # Get current state of boiler
        self.publish(self.boiler)  # Publish data to MQTT broker
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

    def on_log(self, client, userdata, level, buf):
        print(buf)

if __name__ == '__main__':
    mqtt_client = MQTT_Client()
    mqtt_client.publish("Hello World!")
    mqtt_client.run()

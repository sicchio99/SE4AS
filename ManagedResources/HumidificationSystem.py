from threading import Thread
import paho.mqtt.client as mqtt


class HumidificationSystem:

    def __init__(self, section):
        self.section = section
        self.client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        thread = Thread(target=self.mqtt_connection)
        thread.start()

    def mqtt_connection(self):
        self.client_mqtt.connect("mosquitto", 1883)
        self.client_mqtt.on_connect = self.on_connect
        self.client_mqtt.on_message = self.on_message
        self.client_mqtt.on_subscribe = self.on_subscribe
        self.client_mqtt.loop_forever()

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print(f"Broker rejected you subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Connessione MQTT avvenuta con successo")
            client.subscribe(f"executions/{self.section.section_name}/#")
        else:
            print(f"Failed to connect: {rc}. loop_forever() will retry connection")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        execution = payload.split("/")
        print("ON MESSAGE:" + str(execution))
        if execution[1] == 'HUMIDIFY':
            self.increaseHumidity(1)
        elif execution[1] == 'DANGER-H':
            self.increaseHumidity(4)
        elif execution[1] == 'DEHUMIDIFY':
            self.decreaseHumidity(1)
        elif execution[1] == 'DANGER-D':
            self.decreaseHumidity(4)
        elif execution[1] == 'OFF':
            self.constantHumidity()
        else:
            print("Communication error!")

    def increaseHumidity(self, power):
        self.section.humidity = self.section.humidity + power//2
        self.section.fineDust = self.section.fineDust - power
        if self.section.fineDust < 0:
            self.section.fineDust = 0
        if power == 1:
            print(f"Humidification System HUMIDIFY at medium power - {self.section.section_name}")
        else:
            print(f"Humidification System HUMIDIFY at maximum power - {self.section.section_name}")
        self.client_mqtt.publish(f"HumidificationSystem/{self.section.section_name}", "UP")

    def decreaseHumidity(self, power):
        self.section.humidity = self.section.humidity - power
        self.section.fineDust = self.section.fineDust + power//2
        if self.section.humidity < 0:
            self.section.humidity = 0
        if power == 1:
            print(f"Humidification System DEHUMIDIFY at medium power - {self.section.section_name}")
        else:
            print(f"Humidification System DEHUMIDIFY at maximum power - {self.section.section_name}")
        self.client_mqtt.publish(f"HumidificationSystem/{self.section.section_name}", "DOWN")

    def constantHumidity(self):
        print(f"Humidification System OFF - {self.section.section_name}")
        self.client_mqtt.publish(f"HumidificationSystem/{self.section.section_name}", "OFF")


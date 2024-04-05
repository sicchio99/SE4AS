import paho.mqtt.client as mqtt
from threading import Thread


class Windows:

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

    def on_subscribe(client, userdata, mid, reason_code_list, properties):
        if reason_code_list[0].is_failure:
            print(f"Broker rejected you subscription: {reason_code_list[0]}")
        else:
            print(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_connect(self, client, userdata, flags, rc):
        self.client_mqtt.subscribe(f"executions/{self.section.section_name}/#")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        execution = payload.split("/")

        if execution[0] == 'ON':
            self.openWindows()
        elif execution[0] == 'OFF':
            self.closeWindows()

    def openWindows(self):
        self.section.co = self.section.co - 4
        self.section.co2 = self.section.co2 - 4
        print("Windows open")
        self.client_mqtt.publish("Window", "Open")

    def closeWindows(self):
        print("Windows close")
        self.client_mqtt.publish("Window", "Close")

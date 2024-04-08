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
        if execution[0] == 'ON':
            self.openWindows()
        elif execution[0] == 'OFF':
            self.closeWindows()

    def openWindows(self):
        self.section.co -= 1
        if self.section.co < 0:
            self.section.co = 0
        self.section.co2 -= 1
        if self.section.co2 < 0:
            self.section.co2 = 0
        print(f"Windows open - {self.section.section_name}")
        self.client_mqtt.publish(f"Window/{self.section.section_name}", "Open")

    def closeWindows(self):
        print(f"Windows close - {self.section.section_name}")
        self.client_mqtt.publish(f"Window/{self.section.section_name}", "Close")

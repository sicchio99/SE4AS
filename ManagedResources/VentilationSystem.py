from threading import Thread
import paho.mqtt.client as mqtt

class VentilationSystem:

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
            print("Successful MQTT connection")
            client.subscribe(f"executions/{self.section.section_name}/#")
        else:
            print(f"Failed to connect: {rc}. loop_forever() will retry connection")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        execution = payload.split("/")
        print(self.section.section_name, "VENTILATION ON MESSAGE:" + str(execution))
        if execution[0] == 'ON':
            self.activeVentilation(4)
        elif execution[0] == 'DANGER-CO' or execution[0] == 'DANGER-CO2' or execution[0] == 'DANGER-ALL':
            self.activeVentilation(10)
        elif execution[0] == 'OFF':
            self.disableVentilation()
        else:
            print(self.section.section_name, "Communication error!")

    def activeVentilation(self, power):
        self.section.co -= power//2
        if self.section.co < 0:
            self.section.co = 0
        self.section.co2 -= power*5
        if self.section.co2 < 0:
            self.section.co2 = 0
        if power == 4:
            print(f"Ventilation System ON at medium power - {self.section.section_name}")
        else:
            print(f"Ventilation System ON at maximum power - {self.section.section_name}")
        # self.client_mqtt.publish(f"VentilationSystem/{self.section.section_name}", "Active")

    def disableVentilation(self):
        print(f"Ventilation System OFF - {self.section.section_name}")
        # self.client_mqtt.publish(f"VentilationSystem/{self.section.section_name}", "Not Active")


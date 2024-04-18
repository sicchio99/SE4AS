from threading import Thread
import paho.mqtt.client as mqtt


class Alarm:

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

        if execution[0] == 'DANGER' or execution[1] == 'DANGER-D' or execution[1] == 'DANGER-H':
            self.activeAlarm()
        else:
            self.disableAlarm()

    def activeAlarm(self):
        self.section.alarmState = True
        self.client_mqtt.publish(f"Alarm/{self.section.section_name}", "ACTIVE")
        print('ALARM ACTIVATED')

    def disableAlarm(self):
        self.section.alarmState = False
        self.client_mqtt.publish(f"Alarm/{self.section.section_name}", "NOT ACTIVE")
        print('ALARM DEACTIVATED')

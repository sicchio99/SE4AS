from threading import Thread
import paho.mqtt.client as mqtt

class Alarm:

    def __init__(self, section):
        self.section = section
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
        thread = Thread(target=self.mqtt_connection)
        thread.start()

    def mqtt_connection(self):
        self.client.connect("mosquitto", 1883)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe("alarm/#")

    def on_message(self, client, userdata, msg):
        topic = msg.topic.split('/')
        section_name = topic[1]
        condition = topic[2]

        if section_name == self.section.section_name:
            if condition == 'activate':
                self.activeAlarm()
            else:
                self.disableAlarm()

    def activeAlarm(self):
        self.section.alarm_state = True
        print('ALARM ACTIVATED')

    def disableAlarm(self):
        self.section.alarm_state = False
        print('ALARM DEACTIVATED')

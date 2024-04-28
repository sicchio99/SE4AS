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
            print("Successful MQTT connection")
            client.subscribe(f"executions/{self.section.section_name}/#")
        else:
            print(f"Failed to connect: {rc}. loop_forever() will retry connection")

    def check_alarm_status(self, alarms):
        # Iterate through the values in the alarmType dictionary
        for value in alarms.values():
            # If one value is True, return True
            if value:
                return True
        return False

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8")
        execution = payload.split("/")
        print(self.section.section_name, "ALARM ON MESSAGE:" + str(execution))

        if execution[0] == 'DANGER-CO':
            self.activeAlarm(execution[0], 0)
            self.disableAlarm('CO2')
        elif execution[0] == 'DANGER-CO2':
            self.activeAlarm(execution[0], 0)
            self.disableAlarm('CO')
        elif execution[0] == 'DANGER-ALL':
            self.activeAlarm(execution[0], 0)
        elif execution[0] == 'OFF':
            self.disableAlarm('0')

        if execution[1] == 'DANGER-D':
            self.activeAlarm(execution[1], 1)
            self.disableAlarm('H')
        elif execution[1] == 'DANGER-H':
            self.activeAlarm(execution[1], 1)
            self.disableAlarm('D')
        elif execution[1] == 'DANGER-ALL':
            self.activeAlarm(execution[1], 1)
        elif execution[1] == 'OFF':
            self.disableAlarm('1')

    def activeAlarm(self, dangerParameter, payloadPart):
        self.section.alarmState = True
        # self.client_mqtt.publish(f"Alarm/{self.section.section_name}", "ACTIVE")
        if dangerParameter == 'DANGER-CO':
            self.section.alarmType['co'] = True
            print(self.section.section_name, 'ALARM ACTIVATED, CAUSE: CO')
        elif dangerParameter == 'DANGER-CO2':
            self.section.alarmType['co2'] = True
            print(self.section.section_name, 'ALARM ACTIVATED, CAUSE: CO2')
        elif dangerParameter == 'DANGER-ALL' and payloadPart == 0:
            self.section.alarmType['co'] = True
            self.section.alarmType['co2'] = True
            print(self.section.section_name, 'ALARM ACTIVATED, CAUSE: CO AND CO2')
        elif dangerParameter == 'DANGER-H':
            self.section.alarmType['fineDust'] = True
            print(self.section.section_name, 'ALARM ACTIVATED, CAUSE: FINE DUST')
        elif dangerParameter == 'DANGER-D':
            self.section.alarmType['humidity'] = True
            print(self.section.section_name, 'ALARM ACTIVATED, CAUSE: HUMIDITY')
        elif dangerParameter == 'DANGER-ALL' and payloadPart == 1:
            self.section.alarmType['fineDust'] = True
            self.section.alarmType['humidity'] = True
            print(self.section.section_name, 'ALARM ACTIVATED, CAUSE: FINE DUST AND HUMIDITY')
        else:
            print('ALARM ERROR')

    def disableAlarm(self, dangerParameter):

        if dangerParameter == 'CO':
            self.section.alarmType['co'] = False
            print(self.section.section_name, 'co alarm deactivated')
        elif dangerParameter == 'CO2':
            self.section.alarmType['co2'] = False
            print(self.section.section_name, 'co2 alarm deactivated')
        elif dangerParameter == '0':
            self.section.alarmType['co'] = False
            self.section.alarmType['co2'] = False
            print(self.section.section_name, 'co and co2 alarms deactivated')
        elif dangerParameter == 'H':
            self.section.alarmType['fineDust'] = False
            print(self.section.section_name, 'fine dust alarms deactivated')
        elif dangerParameter == 'D':
            self.section.alarmType['humidity'] = False
            print(self.section.section_name, 'humidity alarms deactivated')
        elif dangerParameter == '1':
            self.section.alarmType['fineDust'] = False
            self.section.alarmType['humidity'] = False
            print(self.section.section_name, 'fin dust and humidity alarms deactivated')
        else:
            print(self.section.section_name, 'Disable alarm error')

        alarmState = self.check_alarm_status(self.section.alarmType)
        print("Alarm State", self.section.section_name, alarmState)
        if not alarmState:
            self.section.alarmState = False
            # self.client_mqtt.publish(f"Alarm/{self.section.section_name}", "NOT ACTIVE")

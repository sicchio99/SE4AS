import time
import paho.mqtt.client as mqtt
from random import random
from Section import Section

"""
def publish():
    global mqttc
    while True:
        data = random()
        mqttc.publish("se4as/test/test2", data, qos=1)
        print(f'Published data: {data}')
        time.sleep(5)


if __name__ == '__main__':
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    mqttc.connect("mosquitto", 1883)
    mqttc.loop_start()
    publish()
"""

if __name__ == '__main__':
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)

    sections = []

    section_a = Section(section_name="Section A", co=0, co2=0, fine_dust=0, humidity=0)
    sections.append(section_a)
    section_b = Section(section_name="Section A", co=0, co2=0, fine_dust=0, humidity=0)
    sections.append(section_b)
    section_c = Section(section_name="Section A", co=0, co2=0, fine_dust=0, humidity=0)
    sections.append(section_c)
    #Definizione sezioni

    while True:
        for section in sections:
            section.simulate(client=client_mqtt)

        time.sleep(1)

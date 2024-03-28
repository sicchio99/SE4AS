import time
import paho.mqtt.client as mqtt
from Section import Section


if __name__ == '__main__':
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)

    sections = []

    # Definizione sezioni
    section_a = Section(section_name="Section_a", co=0, co2=0, fineDust=0, humidity=0)
    sections.append(section_a)
    section_b = Section(section_name="Section_b", co=0, co2=0, fineDust=0, humidity=0)
    sections.append(section_b)
    section_c = Section(section_name="Section_c", co=0, co2=0, fineDust=0, humidity=0)
    sections.append(section_c)

    while True:
        for section in sections:
            section.simulate(client=client_mqtt)

        time.sleep(1)

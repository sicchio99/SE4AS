import time
import paho.mqtt.client as mqtt
from Section import Section


if __name__ == '__main__':
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)

    sections = []

    # Definizione sezioni
    section_a = Section(section_name="Section_a", co=7, co2=800, fineDust=10, humidity=32)
    sections.append(section_a)
    section_b = Section(section_name="Section_b", co=20, co2=930, fineDust=20, humidity=40)
    sections.append(section_b)
    # section_c = Section(section_name="Section_c", co=12, co2=650, fineDust=15, humidity=55)
    section_c = Section(section_name="Section_c", co=120, co2=650, fineDust=15, humidity=55)
    sections.append(section_c)

    while True:
        for section in sections:
            section.simulate(client=client_mqtt)

        time.sleep(2)

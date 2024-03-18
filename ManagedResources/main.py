import time
import paho.mqtt.client as mqtt
from random import random


def publish():
    global mqttc
    while True:
        data = random()
        mqttc.publish("se4as/test/test2", data, qos=1)
        print(f'Published data: {data}')
        time.sleep(5)


if __name__ == '__main__':
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.connect("mosquitto", 1883)
    mqttc.loop_start()
    publish()

import paho.mqtt.client as mqtt
import time


def on_connect(client,userdata,flags,rc):
    print("Connected with result code "+str(rc))
    client.subscrive("se4as/test/test2")


def on_message(client, userdata, message):
    global messages
    print(message.payload)
    messages.append(message.payload)


if __name__ == '__main__':
    messages = []
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_message = on_message
    mqttc.connect("mosquitto", 1883)

    mqttc.loop_forever()
    # Ciclo while True per mantenere il client MQTT in esecuzione
    while True:
        if len(messages)>0:
            print("Actual: "+str(messages))
            mqttc.publish("se4as/test/test3", messages[-1], qos=1)
            time.sleep(2)

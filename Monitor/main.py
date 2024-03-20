import paho.mqtt.client as mqtt
import time


def on_connect(self,client,userdata,flags,rc):
    print("Connected with result code "+str(rc))
    client.subscrive("se4as/test/test2")
    return rc


def on_message(client, userdata, message):
    time.sleep(2)
    client.publish("se4as/test/test3", message.payload, qos=1)


if __name__ == '__main__':
    #mqtt_pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    #mqtt_pub.connect("mosquitto", 1883)

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.connect("mosquitto", 1883)
    #mqttc.loop_forever()
    mqttc.loop_start()
    while True:
        a = 1
        print(a)

    # Ciclo while True per mantenere il client MQTT in esecuzione
    #while True:
        #if len(messages)>0:
            #print("Actual: "+str(messages))
            #mqttc.publish("se4as/test/test3", messages[-1], qos=1)
            #time.sleep(2)

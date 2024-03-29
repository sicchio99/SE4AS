import paho.mqtt.client as mqtt
import redis
import time
import json
"""
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("se4as/test/#")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


def on_message(client, userdata, message):
    client.publish("new", message.payload, qos=1)
    client.publish("se4as/test/test3", message.payload, qos=1)


if __name__ == '__main__':
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_subscribe = on_subscribe
    mqttc.connect("mosquitto", 1883)
    mqttc.loop_forever()

"""


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("industry/#")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    chiave = str(msg.topic) + "-grafana"
    # print(str(msg.topic + " -> " + payload))
    # Scrittura nel database
    userdata.set(chiave, payload)

    # Inserisci il valore nella lista associata alla chiave
    # database.rpush(chiave, payload)
    # Aggiungi il timestamp al sorted set
    # database.zadd('timestamps:' + chiave, {payload: time.time()})

    elemento = {'value': payload, 'timestamp': time.time()}
    userdata.lpush(str(msg.topic), json.dumps(elemento)) #lpush aggiunge in testa, rpush in coda

    print(str(msg.topic + " -> " + payload))


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == '__main__':

    # connessione al database
    database = redis.Redis(host='redis', port=6379, db=0)

    # connessione al broker
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=database, reconnect_on_failure=True)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.connect("mosquitto", 1883)
    client_mqtt.loop_forever()


import paho.mqtt.client as mqtt
import redis
import time
import json


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("industry/#")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    key = msg.topic.split("/")
    if key[2] == "alarmState":
        topic = f"alarmState/{key[1]}"
    else:
        topic = str(msg.topic)
    # chiave = str(msg.topic) + "-grafana"
    # print(str(msg.topic + " -> " + payload))
    # Scrittura nel database per grafana
    userdata.set(topic + "-grafana", payload)

    # Inserisci il valore nella lista associata alla chiave
    # database.rpush(chiave, payload)
    # Aggiungi il timestamp al sorted set
    # database.zadd('timestamps:' + chiave, {payload: time.time()})

    elemento = {'value': payload, 'timestamp': time.time()}
    # userdata.lpush(str(msg.topic), json.dumps(elemento)) #lpush aggiunge in testa, rpush in coda
    userdata.lpush(topic, json.dumps(elemento))  # lpush aggiunge in testa, rpush in coda

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


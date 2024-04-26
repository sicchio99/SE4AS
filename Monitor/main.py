import paho.mqtt.client as mqtt
import redis
import time
import json
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from database import Database


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("industry/#")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    key = msg.topic.split("/")
    """
    if key[2] == "alarmState":
        topic = f"alarmState/{key[1]}"
    elif key[2] == "alarmType":
        topic = f"alarmType/{key[1]}"
    else:
        topic = str(msg.topic)

    userdata.set(topic + "-grafana", payload)

    elemento = {'value': payload, 'timestamp': time.time()}
    userdata.lpush(topic, json.dumps(elemento))  # lpush aggiunge in testa, rpush in coda
    """

    # dbWrite(key, payload)
    db.databaseWrite(key, payload)

    print(str(msg.topic + " -> " + payload))


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


"""
def dbWrite(topic, value):
    bucket = "seas"
    org = "univaq"
    token = "seasinfluxdbtoken"
    url = "http://influxdb:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    p = influxdb_client.Point("industry_data").tag("section", topic[1]).field(topic[2], value).time(int(time.time()), "s")
    try:
        write_api.write(bucket=bucket, org=org, record=p)
        print("Scrittura in InfluxDB completata con successo!")

    except Exception as e:
        # Gestisci eventuali errori durante la scrittura
        print(f"Errore durante la scrittura in InfluxDB: {e}")
"""


if __name__ == '__main__':
    # connessione al database
    # database = redis.Redis(host='redis', port=6379, db=0)
    db = Database()

    # connessione al broker
    # client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, userdata=database, reconnect_on_failure=True)
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.connect("mosquitto", 1883)
    client_mqtt.loop_forever()

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("status/#")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    topic = msg.topic.split("/")
    message_key = f"plans/"+topic[1]+"/"+topic[2]
    """
    if payload == actions['esempio1']:
        client_mqtt.publish(message_key, 'increase')
        print(f"{topic[1]}-{topic[2]}: increase")
    if payload == actions['esempio2']:
        client_mqtt.publish(message_key, 'decrease')
        print(f"{topic[1]}-{topic[2]}: decrease")
    if payload == actions['esempio3']:
        client_mqtt.publish(message_key, 'danger - increase')
        print(f"{topic[1]}-{topic[2]}: danger - increase")
    if payload == actions['esempio4']:
        client_mqtt.publish(message_key, 'danger - decrease')
        print(f"{topic[1]}-{topic[2]}: danger - decrease")
    if payload == actions['esempio5']:
        client_mqtt.publish(message_key, 'no more danger')
        print(f"{topic[1]}-{topic[2]}: no more danger")
    """
    if payload == actions['no actions']:
        client_mqtt.publish(message_key, 'no actions')
        print(f"{topic[1]}-{topic[2]}: no actions")
    if payload == actions['decrease']:
        client_mqtt.publish(message_key, 'decrease')
        print(f"{topic[1]}-{topic[2]}: decrease")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == '__main__':

    # Dizionario azione - valore
    actions = {
        'no actions': '0',
        'decrease': '1'
    }

    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.connect("mosquitto", 1883)
    client_mqtt.loop_forever()

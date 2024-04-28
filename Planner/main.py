import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("status/#")


def on_message(client, userdata, msg):

    plan = ""

    payload = msg.payload.decode("utf-8")
    status = payload.split("/")
    topic = msg.topic.split("/")
    message_key = f"plans/"+topic[1]

    for state in status:
        decomposed_state = state.split("-")
        if decomposed_state[1] == '0':
            plan += "/no_actions"
            print(f"{topic[1]} - {decomposed_state[0]}: no_actions")
        elif decomposed_state[1] == '1':
            plan += f"/decrease"
            print(f"{topic[1]} - {decomposed_state[0]}: decrease")
        elif decomposed_state[1] == '2':
            plan += "/danger"
            print(f"{topic[1]} - {decomposed_state[0]}: danger")
        elif decomposed_state[1] == '3':
            plan += "/increase"
            print(f"{topic[1]} - {decomposed_state[0]}: increase")
        else:
            print(f"{topic[1]} - {decomposed_state[0]}: Error")

    # plan = string to publish on the section channel. Format: /string1/string2/string3/string4
    client_mqtt.publish(message_key, plan)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == '__main__':

    # Message broker connection
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.connect("mosquitto", 1883)
    client_mqtt.loop_forever()

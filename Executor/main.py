import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("plans/#")


def on_message(client, userdata, msg):
    executions = ""
    payload = msg.payload.decode("utf-8")
    plan = payload.split("/")
    print(str(plan))
    topic = msg.topic.split("/")
    message_key = f"executions/" + topic[1]

    # Controllo su co e co2
    if plan[1] == "no_actions" and plan[2] == "no_actions":
        executions += "OFF"
        print(f"{topic[1]}: deactive ventilation system and close the windows")
    elif plan[2] == "danger" or plan[2] == "danger":
        executions += "DANGER"
        print(f"{topic[1]}: open the windows, active the ventilation at the maximum power and active the alarm!")
    #elif plan[1] == "decrease" or plan[2] == "decrease":
    else:
        executions += "ON"
        print(f"{topic[1]}: active ventilation system and open partially the windows")


    # Controllo su polveri sottili e umidità
    if plan[3] == "no_actions" and plan[4] == "no_actions":
        executions += "/OFF"
        print(f"{topic[1]}: turn off humidification system")
    elif plan[3] == "decrease" and plan[4] == "no_actions":
        executions += "/HUMIDIFY"
        print(f"{topic[1]}: Turn on the humidification system and humidify the air")
    elif plan[3] == "no_actions" and plan[4] == "decrease":
        executions += "/DEHUMIDIFY"
        print(f"{topic[1]}: Turn on the humidification system and dehumidify the air")
    elif plan[3] == "danger" and plan[4] != "danger":
        executions += "/DANGER-D"
        print(f"{topic[1]}: Dehumidify the air at the maximum power and active the alarm!")
    elif plan[3] != "danger" and plan[4] == "danger":
        executions += "/DANGER-H"
        print(f"{topic[1]}: Humidify the air at the maximum power and active the alarm!")
    else:
        print("ERROR!")


    # Pubblicazione sul canale. Messaggio con struttura: part1/part2
    # part1 : comando agli attuatori relativi a co e co2
    # part2 : comando agli attuatori relativi a fineDust e humidity

    client_mqtt.publish(message_key, executions)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == '__main__':

    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.connect("mosquitto", 1883)
    client_mqtt.loop_forever()

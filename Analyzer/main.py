import redis
import json
import time
import paho.mqtt.client as mqtt
from numpy import mean


def getSectionNames():
    keys = database.keys('industry*')
    section_names = set()
    for key in keys:
        decoded_key = key.decode('utf-8')
        section = decoded_key.split('/')[1]  # Ottengo nome sezione da chiave
        section_names.add(section)  # Aggiungo nome della sezione al set
    return section_names


def getParameterNames():
    params = database.keys('industry*')
    param_names = set()
    for param in params:
        decoded_param = param.decode('utf-8')
        parameter = decoded_param.split('/')[2]  # Ottengo nome parametro
        if not parameter.endswith('-grafana'):  # Aggiungo solo se non termina con '-grafana'
            param_names.add(parameter)
    return param_names


def getParametersData(section_name, param_name):
    key = f'industry/{section_name}/{param_name}'
    # esempio per recuperare solo i primi 60 valori della lista -> DA CAMBIARE
    data = database.lrange(key, 0, 59)
    # Parsing dei valori del JSON e recupero dei valori 'value'
    decoded_data = []
    for item in data:
        json_item = json.loads(item.decode('utf-8'))
        value = json_item['value']
        decoded_data.append(int(value))

    return decoded_data


def getParametersLimit():
    # Recupero del valore JSON dalla chiave "Configuration.js"
    config = None
    while config is None:
        config = database.get("Config_data")
        if config is None:
            print("Data not found. New attempt in 1 second...")
            time.sleep(1)

    # Parsing dei dati JSON e assegnazione a limits
    limits = json.loads(config)
    print("JSON data from Database:", config)
    print("Limitations obtained from parsing JSON data:", limits)

    # Stampa il tipo di dati per ciascun valore dei limiti
    # for key, value in limits.items():
        # print(f"Tipo di dati per il limite di {key}: {type(value)}")

    return limits


def checkLimits(parameters_data, limits):
    # print("LIMITI:")
    # for parameter, limit in limits.items():
        # print(f"{parameter}: limite={limit}")

    for section_name, section_values in parameters_data.items():
        # print("\nVALORI ATTUALI per", section_name, ":")
        for parameter, data in section_values.items():
            print(f"{parameter}: {data}")
            average_value = mean(data)
            print("Mean = ", average_value)
            print("Limit = ", limits[parameter])

            # 0 -> Paramter lower than the limit
            # 1 -> Parameter higher than the limit

            if average_value > limits[parameter]:
                print(f"{parameter} in {section_name} - Greater than the maximum")
                client_mqtt.publish(f"status/{section_name}/{parameter}", 1)
            else:
                print(f"{parameter} in {section_name} - OK")
                client_mqtt.publish(f"status/{section_name}/{parameter}", 0)


if __name__ == '__main__':
    # connessione al database
    database = redis.Redis(host='redis', port=6379, db=0)
    # connessione al broker
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)

    # recupero nomi sezioni
    sections = getSectionNames()
    # recupero dei nomi dei parametri
    parameters = getParameterNames()

    while True:
        # Definizione array che conterrà i valori dei parametri
        parameters_data = {}

        # Recupero dei dati dal database
        for section in sections:
            section_values = {}
            for parameter in parameters:
                data = getParametersData(section, parameter)
                section_values[parameter] = data
            parameters_data[section] = section_values

            # print(section + ': ' + str(parameters_data[section]))

        # check dei limiti
        limits = getParametersLimit()

        # controllo dei limiti e pubblicazione dello stato
        checkLimits(parameters_data, limits)

        time.sleep(5)

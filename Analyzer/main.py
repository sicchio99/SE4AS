import redis
import json
import time
import paho.mqtt.client as mqtt
import sys
import random


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
    # esempio per recuperare solo i primi 10 valori della lista -> DA CAMBIARE
    # per polveri/umidità bisogna fare media dei valori, per altri basterebbe anche solo il primo (?), da discutere
    data = database.lrange(key, 0, 9)
    # Parsing dei valori del JSON e recupero dei valori 'value'
    decoded_data = []
    for item in data:
        json_item = json.loads(item.decode('utf-8'))
        value = json_item['value']
        decoded_data.append(int(value))

    return decoded_data


def getParametersLimit():
    # Recupero del valore JSON dalla chiave "Configuration.js"
    config = database.get("Config_data")

    # Verifica se config non è None
    if config:
        # Parsing dei dati JSON e assegnazione a limits
        limits = json.loads(config)
        print("Dati JSON ottenuti da Redis:", config)
        print("Limiti ottenuti dal parsing dei dati JSON:", limits)

        # Stampa il tipo di dati per ciascun valore dei limiti
        for key, value in limits.items():
            print(f"Tipo di dati per il limite di {key}: {type(value)}")

        return limits
    else:
        print("Nessun dato JSON ottenuto da Redis per i limiti.")
        return None



def checkLimits(parameters_data, limits):
    print("LIMITI:")
    for parameter, limit in limits.items():
        print(f"{parameter}: limite={limit}")


    for section_name, section_values in parameters_data.items():
        print("\nVALORI ATTUALI per", section_name, ":")
        for parameter, data in section_values.items():
            print(f"{parameter}: {data}")


            parameter_lower = parameter.lower()

            # Recupera il limite corrispondente al parametro
            limit = limits.get(parameter_lower)


            if limit is None:
                continue


            max_value = max(data)


            print(f"Valore massimo per {parameter}: {max_value}, Limite: {limit}")

            # Controlla se il valore massimo supera il limite, considerando il parametro specifico
            if max_value > limit:
                if parameter.lower() in ['co', 'co2']:
                    # Attiva la ventilazione e apre le finestre
                    error_message = f"Attivare ventilazione {parameter}, fuori limite massimo. Valore massimo attuale: {max_value}"
                    error_message1 = f"Aprire le finestre {parameter}, fuori limite massimo. Valore massimo attuale: {max_value}"
                elif parameter.lower() == 'finedust':
                    # Attiva l'umidificatore
                    error_message = f"Attivare Umidificatore {parameter}, fuori limite massimo. Valore massimo attuale: {max_value}"



                sys.stderr.write(f"Errore nella sezione {section_name}: {error_message}\n")
                sys.stderr.write(f"Errore nella sezione {section_name}: {error_message1}\n")

def publishStatus(parameters_data, limits, client: mqtt.Client):
    for section_name, section_values in parameters_data.items():
        for parameter, data in section_values.items():
            parameter_lower = parameter.lower()
            limit = limits.get(parameter_lower)
            if limit is None:
                continue
            max_value = max(data)
            if max_value > limit:
                status = 1
            else:
                status = 0
            topic = f"status/{section_name}/{parameter}"
            client.publish(topic, status)
            print(f"Published status {status} for {parameter} in section {section_name} on topic {topic}")



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

            print(section + ': ' + str(parameters_data[section]))

        # check dei limiti
        limits = getParametersLimit()

        # controllo dei limiti e pubblicazione dello stato
        #publishStatus(parameters_data, limits, client_mqtt)
        checkLimits(parameters_data, limits)

        time.sleep(5)



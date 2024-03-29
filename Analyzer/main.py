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
    config = database.get("Configuration.json")
    limits = json.loads(config)
    print("Dati JSON ottenuti da Redis:", config)
    print("Limiti ottenuti dal parsing dei dati JSON:", limits)

    # Inizializzazione del dizionario "limits"
    limits = {}

    if config:
        # Caricamento del JSON e costruzione del dizionario "limits"
        config_data = json.loads(config)
        limits = {
            key: config_data[key] for key in config_data
        }

    return limits


def checkLimits(parameters_data, limits):
    print("LIMITI:")
    for parameter, limit in limits.items():
        print(f"{parameter}: limite={limit}")

    for section_name, section_values in parameters_data.items():
        print("\nVALORI ATTUALI per", section_name, ":")
        for parameter, data in section_values.items():
            print(f"{parameter}: {data}")

            # Recupera il limite corrispondente al parametro
            limit = limits.get(parameter)

            # Se il limite non è definito, passa al prossimo parametro
            if limit is None:
                continue

            # Trova il valore massimo all'interno della lista di dati
            max_value = max(data)

            # Controlla se il valore massimo supera il limite, considerando il parametro specifico
            if parameter in ['CO', 'CO2', 'Fine Dust'] and max_value > limits.get(parameter):
                # Genera il messaggio di errore appropriato in base al parametro
                error_message = f"Attivare ventilazione {parameter}, fuori limite massimo. Valore massimo attuale: {max_value}"

                # Stampa il messaggio di errore su stderr
                sys.stderr.write(f"Errore nella sezione {section_name}: {error_message}\n")

                # Stampa di debug
                print(f"Errore nella sezione {section_name}: {error_message}")


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

        # check_results = checkParameters(parameters_data) scegliere se separare il check da pubblicazione su canale o no
        # publish_data(check_results) se separiamo recuperiamo array dei risultati e lo publichiamo sul canale
        limits = getParametersLimit()

        # caso senza separazione
        checkLimits(parameters_data, limits)

        time.sleep(5)


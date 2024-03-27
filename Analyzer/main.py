"""
import redis
import json
import paho.mqtt.client as mqtt

class Analyzer:
    def __init__(self):
        self.CO_LIMIT = 100
        self.CO2_LIMIT = 500
        self.FINE_DUST_LIMIT = 50

        print("Connecting to Redis...")
        self.db = redis.Redis(host='localhost', port=6379, db=0)
        print("Connected to Redis!")
        print("Connecting to MQTT broker...")
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect("localhost", 1883)
        print("Connected to MQTT broker!")

    def check_limits(self):
        sections = ['Section_a', 'Section_b', 'Section_c']
        for section_name in sections:
            co_key = f"industry/{section_name}/co-grafana"
            co2_key = f"industry/{section_name}/co2-grafana"
            fine_dust_key = f"industry/{section_name}/fineDust-grafana"

            print(f"Retrieving data from Redis for section {section_name}...")
            co_data = self.db.lindex(co_key, 0)
            co2_data = self.db.lindex(co2_key, 0)
            fine_dust_data = self.db.lindex(fine_dust_key, 0)
            print(f"Retrieved data from Redis for section {section_name}!")

            print(f"CO data for {section_name}: {co_data}")
            print(f"CO2 data for {section_name}: {co2_data}")
            print(f"Fine dust data for {section_name}: {fine_dust_data}")

            if co_data and co2_data and fine_dust_data:
                co_value = json.loads(co_data.decode())['value']
                co2_value = json.loads(co2_data.decode())['value']
                fine_dust_value = json.loads(fine_dust_data.decode())['value']

                print(f"CO value for {section_name}: {co_value}")
                print(f"CO2 value for {section_name}: {co2_value}")
                print(f"Fine dust value for {section_name}: {fine_dust_value}")

                if co_value > self.CO_LIMIT:
                    self.publish_alert(section_name, "CO", co_value)
                if co2_value > self.CO2_LIMIT:
                    self.publish_alert(section_name, "CO2", co2_value)
                if fine_dust_value > self.FINE_DUST_LIMIT:
                    self.publish_alert(section_name, "Fine Dust", fine_dust_value)

    def publish_alert(self, section_name, parameter, value):
        topic = f"analyzer/alerts/{section_name}"
        message = f"Attenzione, il valore di {parameter} nella sezione {section_name} è {value} e supera il limite"
        print("Publishing MQTT message...")
        self.mqtt_client.publish(topic, message)
        print("MQTT message published!")

if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.check_limits()
"""

import redis
import json
import time
import paho.mqtt.client as mqtt


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
    # da sostituire con chiamata a DB che recupera
    limits = {
        "co": 100,
        "co2": 500,
        "fineDust": 50,
        "humidity": 80
    }

    return limits


def checkLimits(parameters_data):
    # recupero dei valori massimi dal database (simulato), da capire se oltre max serve anche range e valore di pericolo
    limits = getParametersLimit()
    print(str(limits))
    for section in parameters_data:
        print("section: ", section)


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

        # caso senza separazione
        checkLimits(parameters_data)

        time.sleep(5)

import redis
import json
import time
import paho.mqtt.client as mqtt
import numpy as np
import ast
from sklearn.linear_model import LinearRegression
import influxdb_client
from database import Database


"""
def getSectionNames():
    keys = database.keys('industry*')
    section_names = set()
    for key in keys:
        decoded_key = key.decode('utf-8')
        section = decoded_key.split('/')[1]  # Ottengo nome sezione da chiave
        section_names.add(section)  # Aggiungo nome della sezione al set
    return sorted(section_names)
"""


"""
def getSectionsAndParameters():
    query_api = client.query_api()
    query_section = f'import "influxdata/influxdb/schema" schema.tagValues(bucket: "seas", tag: "section")'
    query_parameter = f'import "influxdata/influxdb/schema" schema.fieldKeys(bucket: "{bucket}")'
    section_results = query_api.query(org=org, query=query_section)
    parameter_results = query_api.query(org=org, query=query_parameter)

    sections_name = []
    for element in section_results.to_values():
        sections_name.append(list(element)[2])

    parameters_name = []
    for element in parameter_results.to_values():
        if list(element)[2] != 'alarmState' and list(element)[2] != 'alarmType' and list(element)[2] != 'value':
            parameters_name.append(list(element)[2])

    return sections_name, parameters_name
"""

"""
def getParameterNames():
    params = database.keys('industry*')
    param_names = set()
    for param in params:
        decoded_param = param.decode('utf-8')
        parameter = decoded_param.split('/')[2]  # Ottengo nome parametro
        if not parameter.endswith('-grafana'):  # Aggiungo solo se non termina con '-grafana'
            param_names.add(parameter)
    return sorted(param_names)
"""

"""
def getParametersData(section_name, param_name):
    key = f'industry/{section_name}/{param_name}'
    # Recupero degli ultimi 60 valori salvati nel database
    data = database.lrange(key, 0, 59)
    # Parsing dei valori del JSON e recupero dei valori 'value'
    decoded_data = []
    for item in data:
        json_item = json.loads(item.decode('utf-8'))
        value = json_item['value']
        if value != '':
            decoded_data.append(int(value))

    return decoded_data
"""

"""
def getParametersDataInflux(section_name, param_name):
    query_api = client.query_api()

    query = f'''
        from(bucket: "{bucket}")
        |> range(start: -60m)
        |> filter(fn: (r) => r["_measurement"] == "industry_data")
        |> filter(fn: (r) => r["section"] == "{section_name}")
        |> filter(fn: (r) => r["_field"] == "{param_name}")
    '''

    result = query_api.query(org=org, query=query)

    decoded_data = []
    for table in result:
        for record in table.records:
            decoded_data.append(int(record.values["_value"]))

    return decoded_data
"""


"""
def getParametersLimit():
    # Recupero del valore JSON dalla chiave "Config_data"
    config = None
    while config is None:
        config = database.get("Config_data")
        if config is None:
            print("Data not found. New attempt in 1 second...")
            time.sleep(1)

    json_data = json.loads(config)
    limits = json_data.get("limits", {})  # Estrae oggetto "limits" dal JSON (default: dizionario vuoto se non trovato)
    dangers = json_data.get("danger", {})
    safe_values = json_data.get("safeValue", {})

    # print("Limiti JSON:", limits)
    # print("Dangers JSON:", dangers)
    # print("Safes JSON:", safe_values)

    return limits, dangers, safe_values
"""


"""
def getParametersLimitInflux():
    query_api = client.query_api()

    query = f'''
        from(bucket: "seas")
        |> range(start: -1h)
        |> filter(fn: (r) => r["configuration"] == "configuration")
        |> filter(fn: (r) => r["_field"] == "value")
        |> last()
    '''
    result = query_api.query(org=org, query=query)
    alarm = []
    for element in result.to_values():
        alarm.append(list(element)[5])

    json_data = json.loads(str(alarm[0]))
    limits = json_data.get("limits", {})  # Estrae oggetto "limits" dal JSON (default: dizionario vuoto se non trovato)
    dangers = json_data.get("danger", {})
    safe_values = json_data.get("safeValue", {})

    return limits, dangers, safe_values
"""


"""
def getSectionAlarm(section_name):
    key = f'alarmState/{section_name}'
    danger = database.lindex(key, 0)
    if danger:
        danger_dict = json.loads(danger.decode('utf-8'))

        # Estrae il valore dalla chiave "value" nel dizionario
        danger_value = danger_dict.get('value')

        return danger_value
    else:
        return None
"""

"""
def getSectionAlarmInflux(section_name, alarm_var):
    query_api = client.query_api()

    query = f'''
           from(bucket: "{bucket}")
           |> range(start: -1h)
           |> filter(fn: (r) => r["_measurement"] == "industry_data")
           |> filter(fn: (r) => r["_field"] == "{alarm_var}")
           |> filter(fn: (r) => r["section"] == "{section_name}")
           |> last()
       '''

    result = query_api.query(org=org, query=query)
    alarm = []
    for element in result.to_values():
        alarm.append(list(element)[5])

    return alarm[0]
"""


def predictNextValues(values, window_size, num_predictions):
    """
    Prevede più valori successivi nella sequenza utilizzando regressione lineare con una finestra mobile.

    Argomenti:
    values (list): Lista di elementi della sequenza storica.
    window_size (int): Dimensione della finestra mobile (numero di elementi passati da utilizzare per la previsione).
    num_predictions (int): Numero di valori successivi da prevedere.

    Ritorna:
    numpy.ndarray: Array di valori previsti per i prossimi elementi nella sequenza.
    """

    # Inverti l'ordine degli elementi nella lista values
    # values = values[::-1]

    # Converti la lista di valori in un array NumPy
    values_array = np.array(values)

    # Prepariamo i dati per la regressione lineare
    X = []
    y = []

    # Creiamo le finestre di dati e i corrispondenti target
    for i in range(len(values_array) - window_size - num_predictions + 1):
        X.append(values_array[i:i + window_size])  # Utilizziamo i valori passati come feature
        y.append(values_array[
                 i + window_size:i + window_size + num_predictions])  # I valori successivi sono i target da prevedere

    X = np.array(X)
    y = np.array(y)

    # Trasformiamo X in un array bidimensionale
    X = X.reshape(-1, window_size)

    # Creiamo un modello di regressione lineare
    model = LinearRegression()

    # Addestriamo il modello sui dati preparati
    model.fit(X, y)

    # Prevediamo i valori successivi nella sequenza
    last_window = values_array[-window_size:]  # Prendiamo gli ultimi elementi come finestra mobile
    next_values = model.predict(last_window.reshape(1, -1))

    return next_values.flatten()


def checkLimits(parameters_data, limits, dangers, safe_values, section_alarm):
    parameter_status = {}

    for section_name, section_values in parameters_data.items():
        # print("\nVALORI ATTUALI per", section_name, ":")
        for parameter, data in section_values.items():
            print(f"{section_name}-{parameter}: {data}")
            predicted_values = predictNextValues(data, window_size=3, num_predictions=2)
            print("Predicted values: ", predicted_values)
            print("Limit = ", limits[parameter])
            print("Danger = ", dangers[parameter])
            print("Safe = ", safe_values[parameter])
            print("ALARM STATE = ", section_alarm[section_name][parameter])

            # 0 -> Parameter in the safe range
            # 1 -> Parameter higher than the limit
            # 2 -> Parameter higher than the danger value
            # 3 -> Parameter lower than the minimum

            tolerance = 2
            print("Valore previsto: ", predicted_values[1])
            if section_alarm[section_name][parameter] is False:
                if predicted_values[1] > (limits[parameter] - tolerance) and predicted_values[1] < (
                        dangers[parameter] - tolerance):
                    print(f"{parameter} in {section_name} - Greater than the maximum")
                    parameter_status[parameter] = f'{parameter}-1'
                elif predicted_values[1] > (dangers[parameter] - tolerance):
                    print(f"{parameter} in {section_name} - Greater than the danger limit! DANGER")
                    parameter_status[parameter] = f'{parameter}-2'
                elif parameter == "humidity" and predicted_values[1] < (limits["lower humidity"] + tolerance):
                    print(f"{parameter} in {section_name} - Lower than the the minimum value")
                    parameter_status[parameter] = f'{parameter}-3'
                else:
                    print(f"{parameter} in {section_name} - OK")
                    parameter_status[parameter] = f'{parameter}-0'
            else:
                if predicted_values[1] <= (safe_values[parameter] + tolerance):
                    print(f"{parameter} in {section_name} - No more danger")
                    parameter_status[parameter] = f'{parameter}-0'
                else:
                    print(f"{parameter} in {section_name} - Greater than the danger limit! DANGER")
                    parameter_status[parameter] = f'{parameter}-2'

        # conversione del dizionario in una stringa nel formato x/y/z/k in cui:
        # x = co - stato
        # y = co2 - stato
        # z = fineDust - stato
        # k = humidity - stato
        parameter_status_value = parameter_status.values()
        status_string = "/".join(parameter_status_value)

        client_mqtt.publish(f"status/{section_name}", status_string)


def checkAlarmActive(dangers_data):
    for section_name, alarm_state in dangers_data.items():
        if alarm_state != 'False':
            return True
    return False


"""
def getSectionParameterAlarm(section_name):
    key = f'alarmType/{section_name}'
    danger = database.lindex(key, 0)
    if danger:
        danger_dict = json.loads(danger.decode('utf-8'))

        # Estrae il valore dalla chiave "value" nel dizionario
        danger_value_str = danger_dict.get('value')
        danger_value = ast.literal_eval(danger_value_str)

        return danger_value
    else:
        return None
"""


if __name__ == '__main__':

    bucket = "seas"
    org = "univaq"
    token = "seasinfluxdbtoken"
    url = "http://influxdb:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

    db = Database()
    print("Connessione al database...")
    # connessione al database
    # database = redis.Redis(host='redis', port=6379, db=0)
    # connessione al broker
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)
    print("Connessione al broker MQTT...")

    # recupero nomi sezioni e parametri
    # sections = getSectionNames()
    sections, parameters = db.getSectionsAndParameters()  # da db influx
    print("SECTIONS:" + str(sections))
    # print("SECTIONS INFLUX!" + str(sections_influx))
    # print("PARAM INFLUX!" + str(parameters_influx))
    # recupero dei nomi dei parametri
    # parameters = getParameterNames()
    print("PARAM:" + str(parameters))

    alarm_active = False  # Inizialmente allarmi spenti

    while True:
        # Dizionario che conterrà i dati recuperati dal DB
        parameters_data = {}
        # Dizionario che conterrà lo stato degli allarmi
        dangers_data = {}
        # Dizionario che conterrà gli allarmi dei prametri per ogni sezione
        section_alarm = {}

        # Recupero dei dati dal database
        for section in sections:
            # dangers_data[section] = getSectionAlarm(section)
            dangers_data[section] = db.getSectionAlarm(section, "alarmState")
            # print("Alarm Redis" + section + ": " + str(dangers_data[section]))
            # print("Alarm Influx" + section + ":" + str(alarmTest))
            # section_alarm[section] = getSectionParameterAlarm(section)
            section_alarm[section] = db.getSectionAlarm(section, "alarmType")
            # print("Alarm type Redis:" + str(section_alarm[section]))
            # print("Alarm type Influx:" + str(alarmTypeTest))
            section_values = {}
            for parameter in parameters:
                # data = getParametersData(section, parameter)
                # data = db.getParametersData(section, parameter)
                data = []
                while len(data) < 5:
                    data = db.getParametersData(section, parameter)
                    if len(data) < 5:
                        print("La lista di dati ha meno di 5 elementi. Riprovando...")
                section_values[parameter] = data
                # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                # print(f"Redis data for {section}-{parameter}: {data}")
                # print(f"Data for {section}-{parameter}: {data}")
                # print(f"InfluxDB data for {section}-{parameter}: {data_influx}")
                # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            parameters_data[section] = section_values

        print("Alarm state:" + str(dangers_data))
        print("Alarm type:" + str(section_alarm))

        alarm_active = checkAlarmActive(dangers_data)  # controllo se una delle 3 sezioni ha l'allarme attivato

        # Recupero dei limiti
        # limits, dangers, safe_values = getParametersLimit()
        limits, dangers, safe_values = db.getParametersLimit()
        # print("Limits:" + str(limits))
        # print("LimitsInflux:" + str(limits_influx))
        # print("Dangers:" + str(dangers))
        # print("DangersInflux:" + str(dangers_influx))
        # print("SafeValues:" + str(safe_values))
        # print("SafeValuesInflux:" + str(safe_values_influx))

        # Controllo dei limiti e pubblicazione dello stato
        checkLimits(parameters_data, limits, dangers, safe_values, section_alarm)

        if alarm_active:
            print("Sampling time = 2")
            time.sleep(2)  # controllo ogni 2 secondi se l'allarme è attivo in 1 delle 3 sezioni
        else:
            time.sleep(4)  # controllo ogni 4 secondi se l'allarme non è attivo
            print("Sampling time = 4")

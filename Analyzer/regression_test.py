import redis
import json
import time
import paho.mqtt.client as mqtt
import numpy as np
from numpy import mean
from sklearn.linear_model import LinearRegression


def getSectionNames():
    keys = database.keys('industry*')
    section_names = set()
    for key in keys:
        decoded_key = key.decode('utf-8')
        section = decoded_key.split('/')[1]  # Ottengo nome sezione da chiave
        section_names.add(section)  # Aggiungo nome della sezione al set
    return sorted(section_names)


def getParameterNames():
    params = database.keys('industry*')
    param_names = set()
    for param in params:
        decoded_param = param.decode('utf-8')
        parameter = decoded_param.split('/')[2]  # Ottengo nome parametro
        if not parameter.endswith('-grafana'):  # Aggiungo solo se non termina con '-grafana'
            param_names.add(parameter)
    return sorted(param_names)


def getParametersData(section_name, param_name):
    key = f'industry/{section_name}/{param_name}'
    # esempio per recuperare solo i primi 60 valori della lista -> DA CAMBIARE
    data = database.lrange(key, 0, 59)
    # Parsing dei valori del JSON e recupero dei valori 'value'
    decoded_data = []
    for item in data:
        json_item = json.loads(item.decode('utf-8'))
        value = json_item['value']
        if value != '':
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

    json_data = json.loads(config)
    limits = json_data.get("limits", {})  # Estrae oggetto "limits" dal JSON (default: dizionario vuoto se non trovato)
    dangers = json_data.get("danger", {})
    safe_values = json_data.get("safeValue", {})

    print("Limiti JSON:", limits)
    print("Dangers JSON:", dangers)
    print("Safes JSON:", safe_values)

    return limits, dangers, safe_values


def getSectionAlarm(section_name):
    key = f'alarmState/{section_name}'
    danger = database.lindex(key, 0)
    if danger:
        # Decodifica la stringa JSON in un dizionario Python
        danger_dict = json.loads(danger.decode('utf-8'))

        # Estrai il valore dalla chiave "value" nel dizionario
        danger_value = danger_dict.get('value')

        return danger_value
    else:
        return None


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
    values = values[::-1]

    # Converti la lista di valori in un array NumPy
    values_array = np.array(values)

    # Prepariamo i dati per la regressione lineare
    X = []
    y = []

    # Creiamo le finestre di dati e i corrispondenti target
    for i in range(len(values_array) - window_size - num_predictions + 1):
        X.append(values_array[i:i+window_size])  # Utilizziamo i valori passati come feature
        y.append(values_array[i+window_size:i+window_size+num_predictions])  # I valori successivi sono i target da prevedere

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


def checkLimits(parameters_data, limits, dangers, safe_values, dangers_data):
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
            print("ALARM STATE = ", dangers_data[section_name])

            # 0 -> Parameter lower than the limit
            # 1 -> Parameter higher than the limit
            # 2 -> Parameter higher than the danger value
            # 3 -> Parameter lower than the no-more-danger value

            if dangers_data[section_name] == 'False':
                if predicted_values[1] > limits[parameter] and predicted_values[1] < dangers[parameter]:
                    print(f"{parameter} in {section_name} - Greater than the maximum")
                    parameter_status[parameter] = f'{parameter}-1'
                elif predicted_values[1] > limits[parameter] and predicted_values[1] > dangers[parameter]:
                    print(f"{parameter} in {section_name} - Greater than the danger limit! DANGER")
                    parameter_status[parameter] = f'{parameter}-2'
                else:
                    print(f"{parameter} in {section_name} - OK")
                    parameter_status[parameter] = f'{parameter}-0'
            else:
                if predicted_values[1] <= safe_values[parameter]:
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
    """
    Verifica se almeno una delle sezioni ha l'allarme attivo.

    Argomenti:
    dangers_data (dict): Dati sugli allarmi per ogni sezione.

    Ritorna:
    bool: True se almeno una delle sezioni ha l'allarme attivo, altrimenti False.
    """
    for section_name, alarm_state in dangers_data.items():
        if alarm_state != 'False':
            return True
    return False


if __name__ == '__main__':
    # connessione al database
    database = redis.Redis(host='redis', port=6379, db=0)
    # connessione al broker
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)

    # recupero nomi sezioni
    sections = getSectionNames()
    print("SECTIONS!" + str(sections))
    # recupero dei nomi dei parametri
    parameters = getParameterNames()
    print("PARAM!" + str(parameters))

    alarm_active = False  # impostiamo che all'inizio gli allarmi sono tutti spenti

    while True:
        # Definizione array che conterrà i valori dei parametri
        parameters_data = {}
        dangers_data = {}

        # Recupero dei dati dal database
        for section in sections:
            dangers_data[section] = getSectionAlarm(section)
            section_values = {}
            for parameter in parameters:
                data = getParametersData(section, parameter)
                section_values[parameter] = data
            parameters_data[section] = section_values

        print("ALLARMI:" + str(dangers_data))

        alarm_active = checkAlarmActive(dangers_data)  # controllo se una delle 3 sezioni ha l'allarme attivato

        # check dei limiti
        limits, dangers, safe_values = getParametersLimit()

        # controllo dei limiti e pubblicazione dello stato
        checkLimits(parameters_data, limits, dangers, safe_values, dangers_data)

        if alarm_active:
            time.sleep(2)  # controllo ogni 2 secondi se l'allarme è attivo in 1 delle 3 sezioni
        else:
            time.sleep(4)  # controllo ogni 4 secondi se l'allarme non è attivo

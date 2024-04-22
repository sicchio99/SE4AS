import redis
import json
import influxdb_client
import time
from influxdb_client.client.write_api import SYNCHRONOUS


def read_json_file(file_name):
    with open(file_name, 'r') as file:
        dati_json = json.load(file)
    return dati_json


def read_json_file_influx(file_name):
    with open(file_name, 'r') as file:
        dati_json = json.load(file)  # Carica i dati JSON dal file

    # Converti i dati JSON in una stringa
    dati_json_string = json.dumps(dati_json)

    return dati_json_string


if __name__ == '__main__':
    # connessione al database
    database = redis.Redis(host='redis', port=6379, db=0)

    file_name = 'Configuration.json'
    configuration_data = read_json_file(file_name)
    influx_configuration_data = read_json_file_influx(file_name)
    database.set('Config_data', json.dumps(configuration_data))

    time.sleep(3)

    bucket = "seas"
    org = "univaq"
    token = "seasinfluxdbtoken"
    url = "http://influxdb:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    p = (influxdb_client.Point("industry_data").tag("configuration", "configuration")
         .field("value", influx_configuration_data).time(int(time.time()), "s"))
    try:
        write_api.write(bucket=bucket, org=org, record=p)
        print("Scrittura in InfluxDB completata con successo!")

    except Exception as e:
        # Gestisci eventuali errori durante la scrittura
        print(f"Errore durante la scrittura in InfluxDB: {e}")



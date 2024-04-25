import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import time


class Database:

    def __init__(self):
        self.bucket = "seas"
        self.org = "univaq"
        self.token = "seasinfluxdbtoken"
        self.url = "http://influxdb:8086/"
        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)

    def databaseWrite(self, topic, value):
        # bucket = "seas"
        # org = "univaq"
        # token = "seasinfluxdbtoken"
        # url = "http://influxdb:8086/"
        # client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        write_api = self.client.write_api(write_options=SYNCHRONOUS)

        p = influxdb_client.Point("industry_data").tag("section", topic[1]).field(topic[2], value).time(
            int(time.time()), "s")
        try:
            write_api.write(bucket=self.bucket, org=self.org, record=p)
            print("Scrittura in InfluxDB completata con successo!")

        except Exception as e:
            # Gestisci eventuali errori durante la scrittura
            print(f"Errore durante la scrittura in InfluxDB: {e}")

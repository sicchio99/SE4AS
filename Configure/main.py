import json
import influxdb_client
import time
from influxdb_client.client.write_api import SYNCHRONOUS


def read_json_file_influx(file_name):
    with open(file_name, 'r') as file:
        json_data = json.load(file)

    # Convert JSON data in a string
    json_data_string = json.dumps(json_data)

    return json_data_string


if __name__ == '__main__':

    file_name = 'Configuration.json'
    configuration_data = read_json_file_influx(file_name)

    # Database connection
    bucket = "seas"
    org = "univaq"
    token = "seasinfluxdbtoken"
    url = "http://influxdb:8086/"
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    p = (influxdb_client.Point("industry_data").tag("configuration", "configuration")
         .field("value", configuration_data).time(int(time.time()), "s"))

    try:
        write_api.write(bucket=bucket, org=org, record=p)
        print("Writing in InfluxDB successfully completed!")

    except Exception as e:
        print(f"Error when writing to InfluxDB: {e}")



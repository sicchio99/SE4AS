import influxdb_client
import json
import ast


class Database:

    def __init__(self):
        self.bucket = "seas"
        self.org = "univaq"
        self.token = "seasinfluxdbtoken"
        self.url = "http://influxdb:8086/"
        self.client = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)

    def getSectionsAndParameters(self):
        query_api = self.client.query_api()
        query_section = f'import "influxdata/influxdb/schema" schema.tagValues(bucket: "seas", tag: "section")'
        query_parameter = f'import "influxdata/influxdb/schema" schema.fieldKeys(bucket: "{self.bucket}")'
        section_results = query_api.query(org=self.org, query=query_section)
        parameter_results = query_api.query(org=self.org, query=query_parameter)

        sections_name = []
        for element in section_results.to_values():
            sections_name.append(list(element)[2])

        parameters_name = []
        for element in parameter_results.to_values():
            if list(element)[2] != 'alarmState' and list(element)[2] != 'alarmType' and list(element)[2] != 'value':
                parameters_name.append(list(element)[2])

        return sections_name, parameters_name

    def getParametersLimit(self):
        query_api = self.client.query_api()

        query = f'''
            from(bucket: "seas")
            |> range(start: -1h)
            |> filter(fn: (r) => r["configuration"] == "configuration")
            |> filter(fn: (r) => r["_field"] == "value")
            |> last()
        '''
        result = query_api.query(org=self.org, query=query)
        alarm = []
        for element in result.to_values():
            alarm.append(list(element)[5])

        json_data = json.loads(str(alarm[0]))
        limits = json_data.get("limits",
                               {})  # Estrae oggetto "limits" dal JSON (default: dizionario vuoto se non trovato)
        dangers = json_data.get("danger", {})
        safe_values = json_data.get("safeValue", {})

        return limits, dangers, safe_values

    def getSectionAlarm(self, section_name, alarm_var):
        query_api = self.client.query_api()

        query = f'''
               from(bucket: "{self.bucket}")
               |> range(start: -1h)
               |> filter(fn: (r) => r["_measurement"] == "industry_data")
               |> filter(fn: (r) => r["_field"] == "{alarm_var}")
               |> filter(fn: (r) => r["section"] == "{section_name}")
               |> last()
           '''

        result = query_api.query(org=self.org, query=query)
        alarm = []
        for element in result.to_values():
            alarm.append(list(element)[5])

        if alarm_var != 'alarmType':
            return alarm[0]
        else:
            alarm_dict = ast.literal_eval(alarm[0])
            return alarm_dict

    def getParametersData(self, section_name, param_name):
        query_api = self.client.query_api()

        query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -60m)
            |> filter(fn: (r) => r["_measurement"] == "industry_data")
            |> filter(fn: (r) => r["section"] == "{section_name}")
            |> filter(fn: (r) => r["_field"] == "{param_name}")
        '''

        result = query_api.query(org=self.org, query=query)

        decoded_data = []
        for table in result:
            for record in table.records:
                decoded_data.append(int(record.values["_value"]))

        return decoded_data

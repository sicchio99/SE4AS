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

from paho.mqtt.client import Client
import random
from random import randint


class Section:

    section_name = ""
    co = 0
    co2 = 0
    fine_dust = 0
    humidity = 0
    alarm_state = False

    def __init__(self, section_name: str, co: int, co2: int, fine_dust: int, humidity: int):
        self.sectionName = section_name
        self.co = co
        self.co2 = co2
        self.fineDust = fine_dust
        self.humidity = humidity
        self.actuators = []

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        if rand == 0:
            self.co = self.co + randint(-1, 1)
            self.co2 = self.co2 + randint(-1, 1)
            self.fineDust = self.fine_dust + randint(-1, 1)
            self.humidity = self.humidity + randint(-1, 1)

        client.publish(f"industry/{self.section_name}/co", self.co)
        client.publish(f"industry/{self.section_name}/co2", self.co2)
        client.publish(f"industry/{self.section_name}/fineDust", self.fine_dust)
        client.publish(f"industry/{self.section_name}/humidity", self.humidity)

        print(f'Publishing simulated data for room {self.section_name}')



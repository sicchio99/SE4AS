from paho.mqtt.client import Client
import random
from random import randint
import Windows
import VentilationSystem
import HumidificationSystem


class Section:

    section_name = ""
    co = 0
    co2 = 0
    fineDust = 0
    humidity = 0

    def __init__(self, section_name: str, co: int, co2: int, fineDust: int, humidity: int):
        self.section_name = section_name
        # self.co = random.randint(0, 500)
        # self.co2 = random.randint(0, 1000)
        # self.fineDust = random.randint(0, 160)
        # self.humidity = random.randint(0, 200)
        self.co = co
        self.co2 = co2
        self.fineDust = fineDust
        self.humidity = humidity
        self.alarmState = False
        self.actuators = [Windows.Windows(self),
                          VentilationSystem.VentilationSystem(self),
                          HumidificationSystem.HumidificationSystem(self)]

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        if rand == 0:

            self.co += random.randint(-1, 3)
            if self.co < 0:
                self.co = 0
            self.co2 += random.randint(-1, 3)
            if self.co2 < 0:
                self.co2 = 0
            self.fineDust += random.randint(-1, 2)
            if self.fineDust < 0:
                self.fineDust = 0
            self.humidity += random.randint(-1, 1)
            if self.humidity < 0:
                self.humidity = 0

            # self.co = min(max(0, self.co), 500)
            # self.co2 = min(max(0, self.co2), 1000)
            # self.fineDust = min(max(0, self.fineDust), 160)
            # self.humidity = min(max(0, self.humidity), 200)

        client.publish(f"industry/{self.section_name}/co", self.co)
        client.publish(f"industry/{self.section_name}/co2", self.co2)
        client.publish(f"industry/{self.section_name}/fineDust", self.fineDust)
        client.publish(f"industry/{self.section_name}/humidity", self.humidity)
        client.publish(f"industry/{self.section_name}/alarmState", self.alarmState)

        print(f'Publishing simulated data for room {self.section_name}')



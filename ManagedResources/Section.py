from paho.mqtt.client import Client
import random
from random import randint
import Windows
import VentilationSystem
import HumidificationSystem
import Alarm


class Section:

    section_name = ""
    co = 0
    co2 = 0
    fineDust = 0
    humidity = 0

    def __init__(self, section_name: str, co: int, co2: int, fineDust: int, humidity: int):
        self.section_name = section_name
        self.co = co
        self.co2 = co2
        self.fineDust = fineDust
        self.humidity = humidity
        self.alarmState = False
        self.alarmType = {'co': False, 'co2': False, 'fineDust': False, 'humidity': False}
        self.actuators = [Windows.Windows(self),
                          VentilationSystem.VentilationSystem(self),
                          HumidificationSystem.HumidificationSystem(self),
                          Alarm.Alarm(self)]

    def simulate(self, client: Client):
        rand = random.randint(0, 9)
        if rand == 0:

            self.co += random.randint(-1, 10)
            if self.co < 0:
                self.co = 0
            self.co2 += random.randint(-1, 100)
            if self.co2 < 0:
                self.co2 = 0
            self.fineDust += random.randint(-1, 5)
            if self.fineDust < 0:
                self.fineDust = 0
            self.humidity += random.randint(-1, 1)
            if self.humidity < 0:
                self.humidity = 0
            if self.humidity > 100:
                self.humidity = 100

        client.publish(f"industry/{self.section_name}/co", self.co)
        client.publish(f"industry/{self.section_name}/co2", self.co2)
        client.publish(f"industry/{self.section_name}/fineDust", self.fineDust)
        client.publish(f"industry/{self.section_name}/humidity", self.humidity)
        client.publish(f"industry/{self.section_name}/alarmState", self.alarmState)
        client.publish(f"industry/{self.section_name}/alarmType", str(self.alarmType))

        print(f'Publishing simulated data for room {self.section_name}')



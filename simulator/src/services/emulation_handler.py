from src.models.api_connector import APIConnector
import os
import random

running = False

def get_data(timestamp, amount):
    data = []
    for i in range(amount):
        timestamp = timestamp + 1
        delay = random.randint(10, 20) * 1000000
        capacity = 100 + i
        loss = 0.01 * i
        data.append(
            {"timestamp" : timestamp, "delay" : delay, "capacity" : capacity, "loss" : loss}
        )
    return data, timestamp

def run_emulation(flags, connection, io):
    api = APIConnector(12345, 600)
    starting_time = 0
    print(api.get_amount())
    os.system("pos_sync")
    while flags["emulation"]:
        if api.read_request() == 0:
            continue
        data, starting_time = get_data(starting_time, api.get_amount())
        api.send_data(data)
    os.system("pos_sync")

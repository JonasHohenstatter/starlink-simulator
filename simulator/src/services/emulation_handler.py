from src.models.api_connector import APIConnector
import os
import random
import subprocess

from src.core.positions import get_positions
from src.core.path_gen import get_path
from src.utils.measurement_utils import distance_to_latency, get_path_length
from src.utils.path_utils import descriptor_path_to_coords
import random

from datetime import datetime, timezone, timedelta


running = False

def get_data(timestamp, desc_path, connection, amount):
    """
    This function is used for all data acquisition for the emulation
    """
    current_desc_path = desc_path
    ms = []
    for ts in range(timestamp, timestamp + amount + 1):
        positions = get_positions(connection.get_constellation(), datetime.now(timezone.utc) + timedelta(seconds=ts))
        latency = random.gauss(0, 0.5)
        if (ts % 15) == 0 or current_desc_path == None:
            current_desc_path = get_path(positions, connection)[1]
            latency += random.gauss(5, 3)
        path_coords_ecef = descriptor_path_to_coords(current_desc_path, positions, connection, False)
        dist = get_path_length(path_coords_ecef)
        latency += distance_to_latency(dist)
        ms.append({"timestamp" : ts, "delay" : round(latency * 1000000), "capacity" : 0, "loss" : 0.0} )
    print(ms)
    return ms
        
def run_emulation(flags, connection, io):
    api = APIConnector(12345, 20)
    starting_time = 0
    desc_path = None
    data = get_data(starting_time, desc_path, connection, api.get_amount())
    starting_time += api.get_amount()
    subprocess.Popen("pos_sync")
    while flags["emulation"]:
        if api.read_request() == 0:
            continue
        data = get_data(starting_time, desc_path, connection, api.get_amount())
        starting_time += api.get_amount()
        api.send_data(data)
    subprocess.Popen("pos_sync")

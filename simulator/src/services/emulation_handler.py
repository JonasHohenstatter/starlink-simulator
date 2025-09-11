from src.models.api_connector import APIConnector
import os
import random
import subprocess

from src.core.positions import get_positions
from src.core.path_gen import get_path
from src.utils.measurement_utils import distance_to_rtt, get_path_length
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
        rtt = 0
        if (ts % 15) == 0 and current_desc_path != None:
            new_desc_path = get_path(positions, connection)
            if not all(x == y for x, y in zip(current_desc_path, new_desc_path)):
                current_desc_path = new_desc_path
                rtt += random.gauss(2,1)
        if current_desc_path == None:
            current_desc_path = get_path(positions, connection)
        path_coords_ecef = descriptor_path_to_coords(current_desc_path, positions, connection, False)
        dist = get_path_length(path_coords_ecef)
        rtt += distance_to_rtt(dist)
        rtt += random.gauss(15, 2) + random.gauss(15, 2)
        ms.append({"timestamp" : ts, "delay" : round(rtt * 1000000), "capacity" : 0, "loss" : 0.0} )
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

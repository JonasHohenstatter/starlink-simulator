from src.models.api_connector import APIConnector
from src.models.users import UserData
import os
import random
import subprocess

from src.core.positions import get_positions
from src.core.path_gen import get_path
from src.utils.measurement_utils import distance_to_rtt, get_path_length
from src.utils.path_utils import descriptor_path_to_coords
import random

from datetime import datetime, timezone, timedelta

import copy
import csv

running = False

def get_data(timestamp, connection, amount):
    """
    This function is used for all data acquisition for the emulation
    """
    current_desc_path = connection.get_descriptor_path()
    ms = []
    for ts in range(timestamp, timestamp + amount):
        positions = get_positions(connection.get_constellation(), datetime.now(timezone.utc) + timedelta(seconds=ts))
        rtt = random.gauss(mu=15, sigma=0.5)
        loss = 0.0
        if (ts % 15) == 0 and current_desc_path != None:
            new_desc_path = get_path(positions, connection)
            if not all(x == y for x, y in zip(current_desc_path, new_desc_path)):
                current_desc_path = new_desc_path
                connection.set_descriptor_path(new_desc_path)
                rtt += max(0,random.gauss(mu=4, sigma=2))
                loss = max(0, random.gauss(20, 2))
        if current_desc_path == None:
            current_desc_path = get_path(positions, connection)
        path_coords_ecef = descriptor_path_to_coords(current_desc_path, positions, connection, False)
        dist = get_path_length(path_coords_ecef)
        rtt += max(0, random.gauss(distance_to_rtt(dist), 0.5))
        ms.append({"timestamp" : ts, "delay" : round(rtt * 1000000), "capacity" : ts, "loss" : loss / 100} )
        with open("output.csv", "a", newline="") as f:  # 'a' = append mode
            writer = csv.writer(f)
            writer.writerow([f"{ts},{round(rtt * 1000000)},{ts},{loss / 100}"])
    return ms

def run_emulation(flags, connection, io):
    amount = 20
    port = 12345
    
    duration = 360
    
    con = copy.deepcopy(connection)
    
    starting_time = 0
    data1 = get_data(starting_time, con, amount)
    starting_time += amount
    data2 = get_data(starting_time, con, amount)
    starting_time += amount
    
    api = APIConnector(port, amount)
    
    
    
    while api.read_request() == 0: continue
    api.send_data(data1)
    while api.read_request() == 0: continue
    api.send_data(data2)

    subprocess.Popen("pos_sync -t start", shell=True)
    
    while flags["emulation"]:
        data = get_data(starting_time, con, amount)
        while api.read_request() == 0: 
            if not flags["emulation"]:
                break
            continue
        starting_time += amount
        api.send_data(data)
        if starting_time >= duration:
            break

    subprocess.Popen("pos_sync -t end", shell=True)
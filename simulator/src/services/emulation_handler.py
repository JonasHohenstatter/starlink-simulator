from src.models.api_connector import APIConnector
import os
import random
import subprocess

from src.core.positions import get_positions
from src.core.path_gen import get_path
from src.core.measurement import get_measurements, generate_latency_graph

from src.utils.path_utils import descriptor_path_to_coords
from src.utils.position_utils import format_coordinates

from datetime import datetime, timezone, timedelta


running = False

def get_data(timestamp, desc_path, connection, amount):
    """
    This function is used for all data acquisition for the emulation
    """
    print("Get dater")
    current_desc_path = desc_path
    ms = []
    for ts in range(timestamp, timestamp + amount + 1):
        positions = get_positions(connection.get_constellation(), datetime.now(timezone.utc) + timedelta(seconds=ts))
        if ts % 15 or current_desc_path == None:
            current_desc_path = get_path(positions, connection)[1]
        path_coords_ecef = descriptor_path_to_coords(current_desc_path, positions, connection, False)
        measurements = get_measurements(connection, path_coords_ecef)
        ms.append(measurements)
        
def run_emulation(flags, connection, io):
    api = APIConnector(12345, 10)
    starting_time = 10
    desc_path = None
    print("AAAAH")
    subprocess.Popen("pos_sync")
    while flags["emulation"]:
        if api.read_request() == 0:
            continue
        data, starting_time = get_data(starting_time, desc_path, connection, api.get_amount())
        api.send_data(data)
    subprocess.Popen("pos_sync")

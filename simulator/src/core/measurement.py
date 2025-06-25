from src.utils.measurement_utils import distance_to_latency, get_path_length
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import random

def update_measurements(connection, path_ecef):
    distance = get_path_length(path_ecef)
    if not connection.has_connection():
        connection.add_measurements({"latency" : 0.0})
        return
    if connection.is_flag("handover"):
        connection.remove_flag("handover")
        measurement = {"latency" : distance_to_latency(distance) + 10}
        connection.add_measurements(measurement)
        return
    measurement = {"latency" : distance_to_latency(distance)}
    connection.add_measurements(measurement)
    return

def generate_latency_graph(connection):
    latencies = connection.get_saved_measurements()["latency"]
    if len(latencies) > 480:
        latencies = latencies[-480:]
        
    x = [i * 0.5 for i in range(len(latencies))]
    
    plt.figure(figsize=(8, 4))
    plt.plot(x, latencies, linewidth=2, linestyle='-', color='blue')
    plt.title("Latency DISH -> SAT -> GS")
    plt.xlabel("Time (s)")
    plt.ylabel("Latency (ms)")
    plt.grid(True)
    plt.ylim(bottom=0) 

    plt.savefig("src/figures/" + connection.get_sid() + ".png")
    plt.close()
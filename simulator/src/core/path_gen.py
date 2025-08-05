"""Core Path feature of the Simulator"""

from src.utils.path_utils import min_euclidean_distance, lla_to_ecef, get_available_satellites, get_available_gs
from src.utils.position_utils import format_coordinates
import numpy as np


def get_path(satellites, connection):
    """Calculates and updates the full path from the dish to a destination."""
    path = []
    descriptor_path = []
    
    if not connection.has_dish():
        return (path, descriptor_path)
    
    ecef_coords = satellites["ecef_coords"]

    dish = connection.get_dish()
    dish_coords = lla_to_ecef(dish["lat"], dish["lng"], 0)
    descriptor_path.append("DISH")

    path.append({"lng" : dish["lng"], "lat" : dish["lat"]})
    
    mask = get_available_satellites(dish_coords, ecef_coords, dish["elevation"])
    available_satellites = ecef_coords[mask]
    if len(available_satellites) == 0:
        # No available satellites => No connection to constellation possible
        return ([], [])

    first_hop_idx = min_euclidean_distance(dish_coords, available_satellites)
    first_hop_coords = np.array(satellites["latlng_coords"])[mask][first_hop_idx]
    first_hop_ecef = np.array(ecef_coords)[mask][first_hop_idx]
    
    descriptor_path.append("SAT_" + str(np.where(mask)[0][first_hop_idx]))
    
    first_hop_lla = {
        "lng" : first_hop_coords[0] if not np.isnan(first_hop_coords[0]) else None, 
        "lat" : first_hop_coords[1] if not np.isnan(first_hop_coords[1]) else None
    }
    path.append(first_hop_lla)
    
    ground_stations = connection.get_gs()

    if ground_stations:
        ground_stations_ecef = [lla_to_ecef(gs["lat"], gs["lng"], 0) for gs in ground_stations]

        mask = get_available_gs(ground_stations_ecef, first_hop_ecef)
        available_gs = np.array(ground_stations_ecef)[mask]
        
        if len(available_gs) != 0:
            last_hop_idx = min_euclidean_distance(first_hop_ecef, available_gs);
            path.append(np.array(ground_stations)[mask][last_hop_idx])
            descriptor_path.append("GS_" + str(np.where(mask)[0][last_hop_idx]))
        
    return (path, descriptor_path)
    


    
"""Core Path feature of the Simulator"""

from src.utils.path_utils import min_euclidean_distance, lla_to_ecef, get_available_satellites
from src.utils.position_utils import format_coordinates
import numpy as np


def get_path(satellites, connection):
    """Calculates and updates the full path from the dish to a destination."""
    path = []
    
    ecef_coords = satellites["ecef_coords"]

    dish = connection.get_dish()
    dish_coords = lla_to_ecef(dish["lat"], dish["lon"], 0)

    path.append({"lon" : dish["lon"], "lat" : dish["lat"]})
    
    mask = get_available_satellites(dish_coords, ecef_coords, dish["elevation"])
    available_satellites = ecef_coords[mask]
    if len(available_satellites) == 0:
        # No available satellites => No connection to constellation possible
        return []

    first_hop_idx = min_euclidean_distance(dish_coords, available_satellites)
    first_hop_coords = np.array(satellites["latlon_coords"])[mask][first_hop_idx]
    
    
    first_hop_lla = {"lon" : first_hop_coords[0] if not np.isnan(first_hop_coords[0]) else None, "lat" : first_hop_coords[1] if not np.isnan(first_hop_coords[1]) else None}
    path.append(first_hop_lla)
    
    ground_stations = connection.get_gs()
    
    if ground_stations:
        path.append(ground_stations[0])
    
    return path

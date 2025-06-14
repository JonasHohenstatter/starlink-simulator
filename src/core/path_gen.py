"""Core Path feature of the Simulator"""

from src.utils.path_utils import min_euclidean_distance, lla_to_ecef, get_available_satellites
import numpy as np


def get_path(satellites, connection):
    """Calculates and updates the full path from the dish to a destination."""
    ecef_coords = satellites["ecef_coords"]

    dish = connection.get_dish()
    dish_coords = lla_to_ecef(dish["lat"], dish["lon"], 0)
    
    mask = get_available_satellites(dish_coords, ecef_coords, dish["elevation"])
    available_satellites = ecef_coords[mask]
    if len(available_satellites) == 0:
        # No satellites available
        return []
    
    closest_idx = min_euclidean_distance(dish_coords, available_satellites)
    return [np.array(satellites["names"])[mask][closest_idx]]

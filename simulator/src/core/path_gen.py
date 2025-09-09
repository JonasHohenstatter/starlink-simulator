"""Core Path feature of the Simulator"""

from src.utils.path_utils import lla_to_ecef, get_available_satellites, get_available_gs_distances, euclidean_distances
import numpy as np

PATH_DROP_ELEVATION_FACTOR = 1.5

def get_path(satellites, connection):
    """
    Generates the optimal path for a given connection through the satellite positions
    """
    if check_path(satellites, connection):
        return connection.get_descriptor_path()
    
    if not connection.has_dish():
        return []
    path = ["DISH"]
    
    """Setting up variables"""
    dish = connection.get_dish()
    ground_stations = connection.get_gs()
    ground_stations_ecef = [lla_to_ecef(gs["lat"], gs["lng"], 0) for gs in ground_stations]
    
    """Drop path if no ground stations are available"""
    if len(ground_stations) == 0:
        return []
    
    ecef_coords = satellites["ecef_coords"]
    dish_coords = lla_to_ecef(dish["lat"], dish["lng"], 0)
    
    """Append Dish to paths"""
    available_satellites_mask = get_available_satellites(dish_coords, ecef_coords, dish["elevation"])
    available_satellites = ecef_coords[available_satellites_mask]
    
    """Check if there are any available satellites"""
    if len(available_satellites) == 0:   
        return []
    
    distances = get_available_gs_distances(ground_stations_ecef, available_satellites)
    mask = distances != np.inf
    connectable_satellites = available_satellites[np.any(mask, axis=1)]
    
    if(len(connectable_satellites) == 0):
        return []
    
    gs_sat_dist = distances[np.any(mask, axis=1)]
    dish_sat_dist = euclidean_distances(dish_coords, connectable_satellites)
    
    summed_distances = dish_sat_dist[:, np.newaxis] + gs_sat_dist

    flat_opt_idx = np.argmin(summed_distances)
    sat_index, gs_index = np.unravel_index(flat_opt_idx, summed_distances.shape)
    
    available_sat_idx = np.where(mask)[0][sat_index]
    original_sat_idx = np.where(available_satellites_mask)[0][available_sat_idx]

    path.append("SAT_" + str(original_sat_idx))
    path.append("GS_" + str(gs_index))
    
    return path

def check_path(satellites, connection):
    """
    Checks if the current path is still valid
    """
    if not connection.has_path() or not connection.has_dish():
        return False
    
    path = connection.get_descriptor_path()
    dish = connection.get_dish()
    ground_stations = connection.get_gs()
    ground_stations_ecef = [lla_to_ecef(gs["lat"], gs["lng"], 0) for gs in ground_stations]
    
    ecef_coords = satellites["ecef_coords"]
    dish_coords = lla_to_ecef(dish["lat"], dish["lng"], 0)
    
    """Check if dish can still see satellite"""
    sat_idx = int(path[1].split("_")[-1])
    sat_coords = ecef_coords[sat_idx]
    
    available_satellites_mask = get_available_satellites(dish_coords, ecef_coords, PATH_DROP_ELEVATION_FACTOR * dish["elevation"])
    
    if not available_satellites_mask[sat_idx]:
        return False
    
    """Check if satellite can still see ground station"""
    gs_idx = int(path[2].split("_")[-1])
    gs_coords = ground_stations_ecef[gs_idx]
    
    available_gs_mask = get_available_gs_distances([gs_coords], [sat_coords])[0] != np.inf
    if not available_gs_mask[0]:
        return False
    
    return True
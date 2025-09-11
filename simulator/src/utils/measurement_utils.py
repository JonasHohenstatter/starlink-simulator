import numpy as np


SPEED_OF_LIGHT = 299_792_458 

def distance_to_rtt(distance):
    """Converts a distance in km to a latency value. """
    c_km_per_ms = (SPEED_OF_LIGHT / 1_000_000) # Converting c from m/s to km/ms
    return (distance / c_km_per_ms) * 2

def get_subpaths_length_ecef(path_ecef):
    """Retrieves the distance of the parts of a path by its ecef coords"""
    if path_ecef == []:
        return np.array([])
    diffs = np.diff(path_ecef, axis=0)
    return np.sqrt(np.sum(diffs ** 2, axis=1))

def get_path_length(path_ecef):
    return np.sum(get_subpaths_length_ecef(path_ecef))
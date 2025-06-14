import numpy as np

def lla_to_ecef(lat_deg, lon_deg, alt):
    # Converts lat lon to ecef
    a = 6378137.0 
    e_sq = 6.69437999014e-3 
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    N = a / np.sqrt(1 - e_sq * np.sin(lat)**2)
    x = (N + alt) * np.cos(lat) * np.cos(lon)
    y = (N + alt) * np.cos(lat) * np.sin(lon)
    z = ((1 - e_sq) * N + alt) * np.sin(lat)
    return np.array([x/1000, y/1000, z/1000])

def euclidean_distances(dish, positions):
    return np.sqrt(np.sum(((positions - dish) ** 2), axis=1))

def min_euclidean_distance(dish, positions):
    positions = np.nan_to_num(positions, nan=0.0)
    return np.argmin(euclidean_distances(dish, positions))

def get_available_satellites(dish, positions, min_elevation_deg):
    """
    Used to find mask that masks the positions to only the available satellites for a dish
    """
    r = positions - dish
    r_norm = r / np.linalg.norm(r, axis=1, keepdims=True)
    up_norm = dish / np.linalg.norm(dish)
    
    angle = np.arccos(np.dot(r_norm, up_norm))
    elevation = 90 - np.degrees(angle)
    mask = elevation >= min_elevation_deg - 5
    return mask
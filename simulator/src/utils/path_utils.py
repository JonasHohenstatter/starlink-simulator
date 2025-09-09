import numpy as np

def lla_to_ecef(lat_deg, lng_deg, alt):
    # Converts lat lng to ecef
    a = 6378137.0 
    e_sq = 6.69437999014e-3 
    lat = np.radians(lat_deg)
    lng = np.radians(lng_deg)
    N = a / np.sqrt(1 - e_sq * np.sin(lat)**2)
    x = (N + alt) * np.cos(lat) * np.cos(lng)
    y = (N + alt) * np.cos(lat) * np.sin(lng)
    z = ((1 - e_sq) * N + alt) * np.sin(lat)
    return np.array([x/1000, y/1000, z/1000])

def euclidean_distances(dish, positions):
    return np.sqrt(np.sum(((positions - dish) ** 2), axis=1))

def get_available_satellites(dish, positions, min_elevation_deg):
    """
    Used to find mask that masks the positions to only the available satellites for a dish
    """
    r = positions - dish
    r_norm = r / np.linalg.norm(r, axis=1, keepdims=True)
    up_norm = dish / np.linalg.norm(dish)
    
    angle = np.arccos(np.dot(r_norm, up_norm))
    elevation = 90 - np.degrees(angle)
    mask = elevation >= min_elevation_deg
    return mask

def get_available_gs(gs, satellite):
    
    gs_to_sat = satellite - gs #(2, 3)
    gs_to_sat_norm = gs_to_sat / np.linalg.norm(gs_to_sat, axis=1, keepdims=True) #(2,3)
    
    gs_norm = gs / np.linalg.norm(gs, axis=1, keepdims=True) #(2,3)

    dot_products = np.sum(gs_to_sat_norm * gs_norm, axis=1)
    angle = np.arccos(dot_products)
    
    elevation = 90 - np.degrees(angle)
    
    return elevation >= 10

def get_available_gs_distances(gs, satellites):
    gs = np.asarray(gs, dtype=float)           
    sats = np.asarray(satellites, dtype=float) 
    sats = sats[:, np.newaxis, :]
    gses = gs[np.newaxis, :, :] 
    
    gs_to_sat = sats - gses       
    gs_norm = gses / np.linalg.norm(gses, axis=2, keepdims=True)
    
    dot = np.sum(gs_to_sat * gs_norm, axis=2)  
    dist = np.linalg.norm(gs_to_sat, axis=2)
    elev = np.arcsin(dot / dist)
    
    available_mask = elev > np.deg2rad(10)
    return np.where(available_mask, dist, np.inf)

def descriptor_path_to_coords(descriptor_path, positions, connection, is_latlon: bool):
    path = []
    for desc in descriptor_path:
        if desc == "DISH":
            dish = connection.get_dish()
            if is_latlon:
                path.append({"lng" : dish["lng"], "lat" : dish["lat"]})
            else:
                path.append(lla_to_ecef(dish["lat"], dish["lng"], 0))
        if desc.startswith("SAT"):
            idx = int(desc.split("_")[-1])
            if is_latlon:
                first_hop_coords = positions["latlng_coords"][idx]
                path.append({
                    "lng" : first_hop_coords[0] if not np.isnan(first_hop_coords[0]) else None, 
                    "lat" : first_hop_coords[1] if not np.isnan(first_hop_coords[1]) else None
                })
            else:
                path.append(positions["ecef_coords"][idx])
        if desc.startswith("GS"):
            idx = int(desc.split("_")[-1])
            gs = connection.get_gs()[idx]
            if is_latlon:
                path.append(gs)
            else:
                path.append(lla_to_ecef(gs["lat"], gs["lng"], 0))
    return path

import numpy as np

def format_coordinates(names, pos, type="latlon"):
    if type == "latlon":
        return [{
            "name" : names[i].strip(), 
            "lon": pos[i][0] if not np.isnan(pos[i][0]) else None, 
            "lat" : pos[i][1] if not np.isnan(pos[i][1]) else None , 
            "alt" : round(pos[i][2] / 1000, 3) if not np.isnan(pos[i][2]) else None
        } for i in range(len(names))]
    elif type == "ecef":
        return [{
            "name" : names[i].strip(), 
            "x": pos[i][0] if not np.isnan(pos[i][0]) else None, 
            "y" : pos[i][1] if not np.isnan(pos[i][1]) else None,
            "z" : pos[i][2] if not np.isnan(pos[i][1]) else None
        } for i in range(len(names)) ]
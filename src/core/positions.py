from sgp4.api import SatrecArray
import numpy as np
import pyproj
from datetime import datetime
from src.services.tle_handler import get_satrec_array
from src.utils.astronomics import get_julian, get_gast

def get_ecef(constellation: SatrecArray, jd):
    """Calculation of all coordinates of a constellation at a given julian time in ecef coordinates"""
    _, r, _ = constellation.sgp4(jd, np.array([0.0]))
    reduced_r = np.squeeze(r, axis=1)
    theta = np.radians(get_gast(jd[0]))
    rotation_matrix = np.array([
        [np.cos(theta),  np.sin(theta), 0],
        [-np.sin(theta), np.cos(theta), 0],
        [0,              0,             1]
    ])
    return reduced_r @ rotation_matrix.T

def get_latlon(ecef_coords):
    """Calculation of all coordinates of a constellation at a given julian time in latitutde and longitude"""
    ecef = pyproj.CRS.from_epsg(4978)
    latlon = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(ecef, latlon, always_xy=True)
    positions = np.apply_along_axis(lambda x: transformer.transform(x[0] * 1000, x[1] * 1000, x[2] * 1000), 1, ecef_coords)
    return positions

def get_positions(constellation: str, utctime: datetime):
    con, names = get_satrec_array(constellation)
    """Formatting of all needed coordinate types:"""
    ecef_coords = get_ecef(con, get_julian(utctime))
    latlon_coords = get_latlon(ecef_coords)
    return {"names": names, "ecef_coords" : ecef_coords, "latlon_coords" : latlon_coords}

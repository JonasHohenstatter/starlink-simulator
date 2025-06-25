import math
import numpy as np
from datetime import datetime, timezone

def get_gast(JD):
    """Implemented after: https://aa.usno.navy.mil/faq/GAST"""
    T = (JD - 2451545.0) / 36525
    GMST = (280.46061837 + 360.98564736629 * (JD - 2451545) + 0.000387933 * T**2 - T**3 / 38710000) % 360
    GMST = GMST % 360
    
    M = math.radians((357.5277233 + 35999.05034 * T) % 360)
    Omega = math.radians((125.04452 - 1934.136261 * T) % 360)
    
    delta_psi = -17.20 * math.sin(Omega) - 1.32 * math.sin(2 * M)
    epsilon = math.radians((84381.406 - 46.836769 * T - 0.0001831 * T**2 +
               0.00200340 * T**3) / 3600)

    EoE = delta_psi * math.cos(epsilon) / 3600 
    return (GMST + EoE) % 360 

def get_julian(time: datetime):
    """Converts a UTC datetime to julian"""
    datetime = time.astimezone(timezone.utc)
    jd = 367 * datetime.year - int((7 * (datetime.year + int((datetime.month + 9) / 12.0))) / 4.0) + int(
        (275 * datetime.month) / 9.0) + datetime.day + 1721013.5 + (
                          datetime.hour + datetime.minute / 60.0 + datetime.second / math.pow(60,
                                                                                  2)) / 24.0 - 0.5 * math.copysign(
        1, 100 * datetime.year + datetime.month - 190002.5) + 0.5
    return np.array([jd])

"""
Is used to fetch the newest version of a TLE file. A new TLE is only fetched, if the cached file is older than 24 hours.
"""

import os
import requests
import time
from pathlib import Path
import re

from sgp4.api import SatrecArray, Satrec

def download_file(url, output):
    response = requests.get(url)
    with open(output, "wb") as file:
        file.write(response.content)
    return response.content.decode()
        
def get_tle_url(constellation):
    if constellation == "iss":
        url = "http://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=tle"
    else:
        url = f"http://celestrak.org/NORAD/elements/gp.php?GROUP={constellation}&FORMAT=tle"
    return url

def fetch_tle(constellation):
    path = f"{Path(__file__).resolve().parents[2]}/data/TLEs/{constellation}.txt"
    if os.path.exists(path) and (time.time() - os.path.getctime(path)) < 86400:
        tle = open(path, "r")
        return tle.read()
    url = get_tle_url(constellation)
    return download_file(url, path)

def get_satrec_array(constellation: str):
    """returns a SatRecArray for a given constellation name"""
    tle = fetch_tle(constellation)     
    tle_list = re.findall(r"(?:.+\n)?1 .+\n2 .+", tle)
    satellites = []
    names = []
    for element in tle_list:
        lines = element.split("\n")
        names.append(lines[0].strip())
        u = lines[1]
        w = lines[2]
        satellites.append(Satrec.twoline2rv(u, w))
    return SatrecArray(satellites), names

"""
Is used to fetch the newest version of a TLE file. A new TLE is only fetched, if the cached file is older than 24 hours.
"""

import os
import requests
import time
from pathlib import Path

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

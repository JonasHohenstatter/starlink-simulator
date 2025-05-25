"""
Main event loop that is used to periodically send out position updates to the frontend
"""
from src.core.positions import get_positions
from datetime import datetime, timezone

def loop(flags, connections, io):
    while flags["running"]:
        constellations = get_active_constellations(connections)
        for constellation in constellations:
            io.emit("constellation_update", get_positions(constellation, datetime.now(timezone.utc), "latlon"), to=constellation)
        io.sleep(1)
    
def get_active_constellations(connections):
    constellations = []
    for connection in connections.values():
        constellation = connection.get_constellation()
        if not constellation in constellations:
            constellations.append(constellation)
    return constellations
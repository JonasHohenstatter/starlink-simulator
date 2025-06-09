"""
Main event loop that is used to periodically send out position updates to the frontend
"""
from src.core.positions import get_positions
from src.core.path_gen import get_path
from datetime import datetime, timezone


positions = {}

def loop(flags, connections, io):
    while flags["running"]:
        constellations = get_active_constellations(connections)
        for constellation in constellations:
            positions[constellation] = get_positions(constellation, datetime.now(timezone.utc), "latlon")
            io.emit("constellation_update", positions[constellation], to=constellation)
        for sid in connections:
            connection = connections[sid]
            if connection.has_dish():
                io.emit("path_update", get_path(connection),to=sid)
        io.sleep(0.5)
    
def get_active_constellations(connections):
    constellations = []
    for connection in connections.values():
        constellation = connection.get_constellation()
        if not constellation in constellations:
            constellations.append(constellation)
    return constellations
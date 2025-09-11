"""
Main event loop that is used to periodically send out position updates to the frontend
"""
from src.core.positions import get_positions
from src.core.path_gen import get_path
from src.utils.path_utils import descriptor_path_to_coords
from src.utils.position_utils import format_coordinates
from datetime import datetime, timezone


UPDATE_INTERVAL = 0.5 
HANDOVER_INTERVAL = 15
positions = {}

def position_loop(flags, connections, io):
    iter_counter = 0
    handover = False
    while flags["running"]:
        iter_counter += 1
        if iter_counter == int(HANDOVER_INTERVAL / UPDATE_INTERVAL):
            iter_counter = 0
            handover = True
        """UPDATE POSITIONS AND SEND TO FRONTEND"""
        constellations = get_active_constellations(connections)
        for constellation in constellations:
            positions[constellation] = get_positions(constellation, datetime.now(timezone.utc))
            io.emit("constellation_update", format_coordinates(positions[constellation]["names"], positions[constellation]["latlng_coords"]), to=constellation)
        for sid, connection in connections.items():
            satellites = positions[connection.get_constellation()]
            if handover or (not connection.has_path()) or connection.is_flag("update"):
                new_path = get_path(satellites, connection)
                connection.set_descriptor_path(new_path)
                connection.remove_flag("update")
            path_coords = descriptor_path_to_coords(connection.get_descriptor_path(), satellites, connection, True)
            io.emit("path_update", path_coords, to=sid)
        handover = False
        io.sleep(UPDATE_INTERVAL)

def get_active_constellations(connections):
    constellations = []
    for connection in connections.values():
        constellation = connection.get_constellation()
        if not constellation in constellations:
            constellations.append(constellation)
    return constellations

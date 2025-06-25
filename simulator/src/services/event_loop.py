"""
Main event loop that is used to periodically send out position updates to the frontend
"""
from src.core.positions import get_positions
from src.core.path_gen import get_path
from src.core.measurement import update_measurements, generate_latency_graph
from src.utils.path_utils import descriptor_path_to_coords

from src.utils.position_utils import format_coordinates
from datetime import datetime, timezone

positions = {}

def position_loop(flags, connections, io):
    while flags["running"]:
        constellations = get_active_constellations(connections)
        for constellation in constellations:
            positions[constellation] = get_positions(constellation, datetime.now(timezone.utc))
            io.emit("constellation_update", format_coordinates(positions[constellation]["names"], positions[constellation]["latlng_coords"]), to=constellation)
        for sid in connections:
            connection = connections[sid]
            satellites = positions[connection.get_constellation()]
            if (not connection.has_path()) or connection.is_flag("update"):
                get_path(satellites, connection)
                connection.remove_flag("update")
            path_coords = descriptor_path_to_coords(connection.get_descriptor_path(), satellites, connection, True)
            path_coords_ecef = descriptor_path_to_coords(connection.get_descriptor_path(), satellites, connection, False)
            update_measurements(connection, path_coords_ecef)
            generate_latency_graph(connection)
            if connection.has_connection():
                io.emit("path_update", path_coords, to=sid)
        io.sleep(0.5)

def path_loop(flags, connections, io):
    while flags["running"]:
        for sid in connections:
            connection = connections[sid]
            constellation = connection.get_constellation()
            old_descriptor_path = connection.get_descriptor_path()
            path_coords = get_path(positions[constellation], connection)
            if connection.has_connection():
                io.emit("path_update", path_coords, to=sid)
            if old_descriptor_path != connection.get_descriptor_path():
                connection.set_flag("handover")
        io.sleep(15)

def get_active_constellations(connections):
    constellations = []
    for connection in connections.values():
        constellation = connection.get_constellation()
        if not constellation in constellations:
            constellations.append(constellation)
    return constellations

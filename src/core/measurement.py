from src.utils.measurement_utils import distance_to_latency, get_path_length


def get_measurements(connection, path_ecef):
    distance = get_path_length(path_ecef)
    if connection.is_flag("handover"):
        connection.remove_flag("handover")
        return {"latency" : distance_to_latency(distance) + 10}
    return {"latency" : distance_to_latency(distance)}
import socket
import struct

class APIConnector:
    def __init__(self, port, amount):
        self.sock = socket.create_connection(("127.0.0.1", port))
        self.sock.setblocking(False)
        self.amount = amount
        self.sock.sendall(struct.pack("<I", amount))
    def read_request(self):
        try:
            req = self.sock.recv(10).decode()
            if req.startswith("SEND"):
                return int(req.split()[1])
        except BlockingIOError:
            return 0
    def send_data(self, data):
        data_processing = [
            (entry["timestamp"], entry["delay"], entry["capacity"], entry["loss"]) for entry in data
        ]
        self.sock.sendall(b''.join(struct.pack("<QQQf4x", *entry) for entry in data_processing))
    def get_amount(self):
        return self.amount
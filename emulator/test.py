import socket
import struct

CONNECTION_DATA_AMOUNT = 600

def get_connection_data(amount):
    data = []
    for i in range(amount):
        timestamp = 10 + i
        delay = 10 * i
        capacity = 100 + i
        loss = 0.01 * i
        data.append((timestamp, delay, capacity, loss))
    return b''.join(struct.pack("<QQQf4x", *entry) for entry in data)

HOST = "127.0.0.1"
PORT = 12345

s = socket.create_connection((HOST, PORT))
s.sendall(struct.pack("<I", CONNECTION_DATA_AMOUNT))

while True:
    req = s.recv(10).decode()
    print(req)
    if req.startswith("SEND"):
        amount = int(req.split()[1])
        s.sendall(get_connection_data(amount))
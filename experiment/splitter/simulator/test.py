import socket
import struct
import random

CONNECTION_DATA_AMOUNT = 100

def get_connection_data(starter, amount):
    data = []
    for i in range(amount):
        timestamp = starter + i
        delay = random.randint(20, 45) * 1000000 # Simulating a delay in milliseconds
        capacity = 1000000000000000
        loss = 0
        data.append((timestamp, delay, capacity, loss))
    print(data)
    return b''.join(struct.pack("<QQQf4x", *entry) for entry in data)

HOST = "127.0.0.1"
PORT = 12345

s = socket.create_connection((HOST, PORT))
s.sendall(struct.pack("<I", CONNECTION_DATA_AMOUNT))

starter = 0
while True:
    req = s.recv(10).decode()
    print(req)
    if req.startswith("SEND"):
        amount = int(req.split()[1])
        s.sendall(get_connection_data(starter, amount))
        starter += amount

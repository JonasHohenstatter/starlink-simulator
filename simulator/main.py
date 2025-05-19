# !/usr/bin/env python3

"""
The main implementation of the simulator backend. 
Implements a Socket.io Websocket that supplies the frontend with satellite data
"""

from flask import Flask, request
from flask_socketio import SocketIO, join_room
from flask_cors import CORS
import os

from src.services.eventloop import loop
from src.models.users import UserData

app = Flask(__name__)
CORS(app)
io = SocketIO(app , cors_allowed_origins="*")

flags = {"running" : False}
connections = {}

@io.on("connect")
def connect_handler():
    print("Connectee")
    if not flags["running"]:
        flags["running"] = True
        io.start_background_task(loop, flags, connections, io)

@io.on("disconnect")
def disconnect_handler():
    flags["running"] = False
    del connections[request.sid]
    
@io.on("join_constellation")
def join_constellation(room):
    connections[request.sid] = UserData(room)
    join_room(room)

if __name__ == '__main__':
    io.run(app, port=os.environ.get("PORT", 1234))
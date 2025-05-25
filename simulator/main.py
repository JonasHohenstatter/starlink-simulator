# !/usr/bin/env python3

"""
The main implementation of the simulator backend. 
Implements a Socket.io Websocket that supplies the frontend with satellite data
"""

from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from flask_socketio import join_room
from src.services.event_loop import loop
from flask import request
from src.models.users import UserData

app = Flask(__name__, static_folder="static")
CORS(app)
flags = {"running" : False}
connections = {}

"""Serving the Frontend"""
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

"""Socket setup and handling"""
io = SocketIO(app , cors_allowed_origins="*")

@io.on("connect")
def connect_handler():
    if not flags["running"]:
        flags["running"] = True
        io.start_background_task(loop, flags, connections, io)

@io.on("disconnect")
def disconnect_handler():
    flags["running"] = False
    try:
        del connections[request.sid]
    except KeyError:
        pass
        
@io.on("join_constellation")
def join_constellation(room):
    connections[request.sid] = UserData(room)
    join_room(room)

if __name__ == '__main__':
    io.run(app, port=os.environ.get("PORT", 1234))
# !/usr/bin/env python3

"""
The main implementation of the simulator backend. 
Implements a Socket.io Websocket that supplies the frontend with satellite data
"""

from flask import Flask, send_from_directory, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from flask_socketio import join_room, leave_room

from src.services.event_loop import position_loop
from src.services.gs_handler import load_from_config
from src.services.emulation_handler import run_emulation

from src.utils.api_utils import is_testbed

from flask import request
from src.models.users import UserData

app = Flask(__name__, template_folder="client", static_folder="client")
CORS(app)
flags = {"running" : False, "emulation" : False}
connections = {}

"""Serving the Frontend"""
@app.route("/")
def index():
    return render_template("index.html", testbed=is_testbed())

"""Socket setup and handling"""
io = SocketIO(app , cors_allowed_origins="*")

@io.on("connect")
def connect_handler():
    connections[request.sid] = UserData("starlink")
    connections[request.sid].set_sid(request.sid)
    if not flags["running"]:
        flags["running"] = True
        io.start_background_task(position_loop, flags, connections, io)
    
@io.on("disconnect")
def disconnect_handler():
    flags["running"] = False
    try:
        del connections[request.sid]
    except KeyError:
        pass
    
"""
Event Handlers for the control elements
"""
    
@io.on("ctrl_dish_update")
def dish_update(payload):
    connections[request.sid].set_dish(payload)
    connections[request.sid].set_flag("update")
    
@io.on("ctrl_gs_update")
def gs_update(payload):
    connections[request.sid].set_gs(payload["stations"])
    connections[request.sid].set_flag("update")
    
@io.on("ctrl_gs_load_config")
def gs_load_config(payload):
    ground_stations = load_from_config(payload["configname"])
    connections[request.sid].push_gs(ground_stations)
    io.emit("gs_update", ground_stations, to=request.sid)
    connections[request.sid].set_flag("update")
        
@io.on("ctrl_join_constellation")
def join_constellation(room):
    leave_room(connections[request.sid].get_constellation())
    connections[request.sid].set_constellation(room)
    join_room(room)
    connections[request.sid].set_flag("update")

@io.on("ctrl_start_emulation")
def start_emulation():
    if not flags["emulation"]:
        print("Emulation start")
        flags["emulation"] = True
        io.start_background_task(run_emulation, flags, connections[request.sid], io)
        
@io.on("ctrl_stop_emulation")
def stop_emulation():
    if flags["emulation"]:
        flags["emulation"] = False

if __name__ == '__main__':
    io.run(app, host="0.0.0.0", port=os.environ.get("PORT", 1234), debug=True, allow_unsafe_werkzeug=True)
#!/bin/bash

set -e
set -x

cd /root

# Setup and startup of simulator
apt-get update
apt-get install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r /root/implementation/requirements.txt
#pos_run simulator -- taskset -c 1 python3 /root/implementation/simulator/app.py 

echo "Simulator started"

pos_run delayer -- taskset -c 1 /root/moongen/build/MoonGen /root/implementation/emulator/moonem.lua 0 0 --port 12345 --api

sleep 5

echo "delayer started"

# Experiment starten:
# API pipeline starten und pos syncen

# Experiment beenden
# pos_sync und pipeline stoppen.

pos_sync



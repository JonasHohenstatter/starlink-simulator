#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# # log every command
set -x

apt-get update
apt-get install -y python3-venv python3-pip
python3 -m venv venv
pip install -r implementation/emulator/utilities/requirements.txt
source venv/bin/activate

pos_sync

pos_run loadgen -- taskset -c 1 /root/moongen/build/MoonGen /root/implementation/emulator/lua/l2-load-latency-graph.lua 0 0 -r 1000

pos_sync

pos_kill loadgen

python3 implementation/emulator/utilities/timestamp_graph.py

pos_upload /root/latency_plot.jpg

echo "experiment successful"

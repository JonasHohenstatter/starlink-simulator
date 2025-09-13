#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# # log every command
set -x

apt-get update
apt-get install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r /root/implementation/experiment/legacy/loadgen/lua/utilities/requirements.txt

sleep 5

pos_sync

pos_run loadgen -- taskset -c 1 /root/moongen/build/MoonGen /root/implementation/experiment/legacy/loadgen/lua/l2-load-latency-graph.lua 0 0 -r 1000

pos_sync

pos_kill loadgen --force-upload

python3 /root/implementation/experiment/legacy/loadgen/lua/utilities/timestamp_graph.py

pos_upload /root/latency_plot.jpg

echo "experiment successful"

#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# # log every command
set -x

# wait for experiment to start
pos_sync -t start

sleep 10
# start capturing
pos_run capture -- taskset -c 1 /root/moongen/build/MoonGen /root/implementation/experiment/splitter/capture/lua/capture.lua 1 0 --seq-offset 42 -t 1

# wait for load generator to stop
pos_sync -t end

# wait for traffic to stop and kill capture process
sleep 10
pos_kill capture --force-upload

# wait for capture to stop
sleep 5
chrt 1 taskset -c 1-31 /root/implementation/experiment/splitter/capture/processing/process.sh

apt-get update
apt-get install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r /root/implementation/experiment/splitter/capture/processing/graph/requirements.txt

folder_name="$1_measurement_$(date +"%Y-%m-%d_%H-%M-%S")"

python3 /root/implementation/experiment/splitter/capture/processing/graph/draw_graph.py latency_average.csv loss_over_time.csv "$folder_name"

pos_upload -r /root/"$folder_name"
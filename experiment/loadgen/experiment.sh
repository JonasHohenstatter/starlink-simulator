#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# # log every command
set -x

pos_sync

echo "runnig lg."
pos_run loadgen -- taskset -c 1 /root/moongen/build/MoonGen /root/moongen/examples/l2-load-latency.lua 0 0 -r 1000

pos_sync

pos_kill loadgen

pos_upload /root/histogram.csv

echo "experiment successful"

#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# # log every command
set -x

pos_run loadgen -- taskset -c 1 /root/moongen/build/MoonGen /root/implementation/experiment/splitter/loadgen/lua/pktgen.lua 0 0 -r 1000 -s 64

# Double pos_sync to make unlisted pos_sync work
pos_sync -t start
pos_sync -t end
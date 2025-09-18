#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# # log every command
set -x

cd /root

pos_sync -t start

sleep 5

pos_run loadgen -- taskset -c 16 /root/moongen/build/MoonGen /root/implementation/experiment/splitter/loadgen/lua/pktgen.lua 0 0 -r 1000 -s 64

pos_sync -t end

pos_kill --force-upload loadgen

pos_sync -t cleanup
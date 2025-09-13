#!/bin/bash


set -e

set -x

pos_sync -t start

pos_run capture -- taskset -c 1 /root/moongen/build/MoonGen /root/implementation/experiment/splitter/capture/lua/capture.lua 1 0 --seq-offset 42 -t 1

pos_sync -t end

sleep 5
pos_kill capture
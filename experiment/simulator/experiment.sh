#!/bin/bash

set -e
set -x

cd /root

# Setup and startup of simulator
apt-get update
apt-get install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r implementation/requirements.txt
pos_run simulator python3 /root/implementation/simulator/app.py 

echo "Simulator started"

pos_sync


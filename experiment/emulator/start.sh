#!/usr/bin/env bash

apt update
apt install python3-pip
apt install -y python3-venv

python3 -m venv /home/venv
source /home/venv/bin/activate

pip install -r /home/implementation/requirements.txt
python3 /home/implementation/simulator/app.py
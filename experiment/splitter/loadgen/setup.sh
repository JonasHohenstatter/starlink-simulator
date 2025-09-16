#!/bin/bash

# Script is run locally on experiment server.

# exit on error
set -e
# log every command
set -x

cd /root

# install ice ddp package
git clone https://gitlab+deploy-token-1810:REDACTED@gitlab.lrz.de/idp-lachnit/ice.git -b ice-1.11.14
mkdir -p /lib/firmware/updates/intel/ice/ddp
cp /root/ice/ddp/ice-1.3.30.0.pkg /lib/firmware/updates/intel/ice/ddp/
(cd /lib/firmware/updates/intel/ice/ddp && ln -sf ice-1.3.30.0.pkg ice.pkg)

# install moongen dependencies
apt-get update
apt-get install -y meson ninja-build pkg-config python3-pyelftools libsystemd-dev

# install moongen
cd /root
git clone https://moongen:REDACTED@gitlab.lrz.de/moongen/moongen.git
cd /root/moongen
git checkout v22.11
echo "moongen commit hash: $(git rev-parse HEAD)"
chrt 1 taskset -c 1-31 ./build.sh --noBind
./setup-hugetlbfs.sh

# bind ports to igb_uio driver
python3 /root/moongen/libmoon/deps/dpdk/usertools/dpdk-devbind.py --bind=igb_uio 38:00.1

echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKLIbOqRkWcEIfZV7BYrtyv8km97iNYGea8a1HRmb85Y jonashohenstatter@MacBook-Air-von-Jonas-2.local" >> ~/.ssh/authorized_keys
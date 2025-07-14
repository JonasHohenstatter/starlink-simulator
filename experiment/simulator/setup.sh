#!/bin/bash

set -e
set -x

cd /root

# install ice ddp package
rm -rf /root/ice
rm -rf /root/venv
rm -rf /root/moongen

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
chrt 1 taskset -c 1-31 ./build.sh --noBind
./setup-hugetlbfs.sh

# unmount 2MB Hugepages
umount /dev/hugepages || true

# setup 1G hugepages
for i in {0..7}
do
	if [[ -e "/sys/devices/system/node/node$i" ]]
	then
		echo 16 > /sys/devices/system/node/node$i/hugepages/hugepages-1048576kB/nr_hugepages
	fi
done
mkdir /mnt/hugepages1G || true
mount -t hugetlbfs -o pagesize=1G none /mnt/hugepages1G

python3 /root/moongen/libmoon/deps/dpdk/usertools/dpdk-devbind.py --bind=igb_uio ens2f1 || true

# Build Moonem
cd /root/implementation/emulator
./build.sh
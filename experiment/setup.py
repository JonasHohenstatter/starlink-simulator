import argparse
import logging

import poslib as pos
import os
from pathlib import Path
global log

IMPLEMENTATION_BASE = "/home"

def get_nodes():
    return [el["id"] for el in pos.nodes.list_all()[0]]

def allocate_nodes(nodes, duration):
    try:
        for node in nodes:
            pos.allocations.free(node)
        pos.allocations.allocate(nodes, duration=5)
    except:
        log.error("unable to allocate nodes")
    
def setup_logger():
    global log
    log = logging.getLogger('setup')
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)
    
def setup_emulator(emulator):
    implementation_path = Path(__file__).resolve().parents[1]
    pos.nodes.copy(emulator, implementation_path, IMPLEMENTATION_BASE, recursive=True)
    pos.nodes.bootstrap(emulator)
    with open("emulator/setup.sh", "rb") as setupfile:
        caa = pos.commands.launch(emulator, infile=setupfile)
        print(caa)

def boot_nodes(nodes, image):
    for node in nodes:
        pos.nodes.image(node, image)
        log.info('%s image setup completed', node)
        pos.nodes.reset(node)
        log.info('%s booted', node)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('emulator', choices=get_nodes())
    parser.add_argument('loadgen', choices=get_nodes())
    parser.add_argument('-d', '--duration', type=int, default=15)
    parser.add_argument('-i', '--image', default="debian-bookworm")
    parser.add_argument('-n', '--no-boot', action="store_true")
    args = parser.parse_args()

    setup_logger()
    
    if not args.no_boot:
        nodes = [args.emulator, args.loadgen]
        allocate_nodes(nodes, args.duration)
        boot_nodes(nodes, args.image)
    setup_emulator(args.emulator)
        

if __name__ == "__main__":
    
    main()

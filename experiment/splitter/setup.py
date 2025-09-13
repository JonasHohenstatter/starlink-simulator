import argparse
import logging

import poslib as pos
import os
from pathlib import Path
global log

IMPLEMENTATION_BASE = "/root/"
IMPLEMENTATION_PATH = Path(__file__).resolve().parents[2]
MOONGEN_PATH =  Path(__file__).resolve().parents[2] / "moongen"
EXPERIMENT_PATH = "experiment/splitter"

def get_nodes():
    return [el["id"] for el in pos.nodes.list_all()[0]]

def allocate_nodes(nodes, duration):
    try:
        for node in nodes:
            pos.allocations.free(node)
        if duration == 0:
            pos.allocations.allocate(nodes)
        else:
            pos.allocations.allocate(nodes, duration=duration)
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
    
def setup_node(node, identifier):
    pos.nodes.copy(node, IMPLEMENTATION_PATH, IMPLEMENTATION_BASE, recursive=True)
    pos.nodes.bootstrap(node)
    with open(f"{IMPLEMENTATION_PATH}/{EXPERIMENT_PATH}/{identifier}/setup.sh", "rb") as setupfile:
        pos.commands.launch(node, infile=setupfile, blocking=True)
    log.info('%s Setup on %s completed!', identifier, node)
    
def start_emulator(emulator):
    with open(f"{IMPLEMENTATION_PATH}/{EXPERIMENT_PATH}/simulator/experiment.sh", "rb") as setupfile:
        pos.commands.launch(emulator, infile=setupfile, blocking=True)
    log.info('Started Simulator on %s', emulator)
    
def start_loadgen(loadgen):
    with open(f"{IMPLEMENTATION_PATH}/{EXPERIMENT_PATH}/loadgen/experiment.sh", "rb") as setupfile:
        pos.commands.launch(loadgen, infile=setupfile, blocking=True)
    log.info('Started Loadgen on %s', loadgen)

def boot_nodes(nodes, image):
    for node in nodes:
        pos.nodes.image(node, image)
        log.info('%s image setup completed', node)
        pos.nodes.bootparameters(node, ["iommu=pt"], "")
        pos.nodes.reset(node)
        log.info('%s booted', node)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--duration', type=int, default=0)
    parser.add_argument('-i', '--image', default="debian-bookworm")
    parser.add_argument('-n', '--no-boot', action="store_true")
    args = parser.parse_args()

    setup_logger()

    if not args.no_boot:
        nodes = ["avax", "pact", "stoi"]
        allocate_nodes(nodes, args.duration)
        boot_nodes(nodes, args.image)
    setup_node("stoi", "simulator")
    setup_node("avax", "loadgen")
    setup_node("pact", "capture")

if __name__ == "__main__":
    main()

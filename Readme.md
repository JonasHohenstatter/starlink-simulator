# Starlink Simulator / Emulator

A satellite network simulator (Python, web UI) that drives a MoonGen-based link emulator (MoonEm). Measurements run on the i8 testbed.

| Folder | Contents |
|---|---|
| [simulator/](simulator/) | Flask + Socket.IO backend and web frontend that compute satellite positions, paths and delays |
| [emulator/](emulator/) | MoonEm link emulator (Lua + C++ on MoonGen/DPDK), controlled by the simulator through an API on port `12345` |
| [experiment/](experiment/) | pos testbed scripts: `splitter/` (current setup) and `legacy/` (older 2-node setup) |

## 1. Run the simulator locally

No emulator is needed. This is useful for working on the UI or the path logic.

```bash
cd simulator
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open <http://localhost:1234> (change the port with `PORT=...`). TLE data comes from Celestrak and is cached for 24 h in `simulator/data/TLEs/`.

## 2. Run the full experiment on the testbed

### Prerequisites

- Access to the i8 testbed with `poslib` (the pos Python library) available
- A repo checkout named `implementation` (the scripts expect it at `/root/implementation` on the nodes)
- A `.env` file in the repo root (git ignores it, so it never gets pushed) containing the GitLab clone URLs for MoonGen and the ice DDP package:

  ```bash
  ICE_CLONE_URL=https://<user>:<token>@gitlab.lrz.de/idp-lachnit/ice.git
  MOONGEN_CLONE_URL=https://<user>:<token>@gitlab.lrz.de/moongen/moongen.git
  ```

### Setup (allocate, boot, install)

```bash
python3 experiment/splitter/setup.py            # allocate + boot + set up all nodes
python3 experiment/splitter/setup.py -n         # skip allocation/boot, only re-run setup
python3 experiment/splitter/setup.py -d 120     # allocate for a specific duration
```

This copies the repo to every node and runs that node's `setup.sh`. The scripts clone and build MoonGen, install the ice DDP package, bind the NICs to DPDK, and build the emulator or capture tools.

| Node | Role | Setup script |
|---|---|---|
| `stoi` | simulator + emulator | [experiment/splitter/simulator/setup.sh](experiment/splitter/simulator/setup.sh) |
| `avax` | load generator | [experiment/splitter/loadgen/setup.sh](experiment/splitter/loadgen/setup.sh) |
| `pact` | capture + evaluation | [experiment/splitter/capture/setup.sh](experiment/splitter/capture/setup.sh) |

### Run a measurement

Launch each node's `experiment.sh` on that node via pos, all at the same time. The scripts coordinate with each other through `pos_sync`.

| Node | Script | What it does |
|---|---|---|
| `stoi` | [simulator/experiment.sh](experiment/splitter/simulator/experiment.sh) | Starts MoonEm (`--api`) and the simulator web app |
| `avax` | [loadgen/experiment.sh](experiment/splitter/loadgen/experiment.sh) | Sends 64 B packets at 1000 Mbit/s |
| `pact` | [capture/experiment.sh](experiment/splitter/capture/experiment.sh) `<name>` | Captures traffic, then computes latency/loss and plots them |

Once the simulator is running, open its web UI on `stoi`, port `1234` (e.g. through an SSH tunnel). Set the dish and ground stations, then click **Start emulation**. The simulator then sends the computed delay and loss values to MoonEm.

### Results

The capture node writes `latency_average.csv` and `loss_over_time.csv` and renders plots into `<name>_measurement_<timestamp>/`. That folder is uploaded to the pos results.

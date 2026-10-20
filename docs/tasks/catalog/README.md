# The big catalogue: 100+ PC and server parts

The game today sells about 20 parts. These tasks grow that to **well over 100**: the most popular PC and server parts of
today, across many brands, colours, RGB and non-RGB, and every common capacity.

Each task file below is one part family. Each family runs as its own cloud session on its own branch.

| Task | Family | About |
|---|---|---|
| `10-cpus.md` | CPUs | 14 (10 desktop, 4 server) |
| `11-gpus.md` | Graphics cards | 15 (13 desktop, 2 data-centre accelerators) |
| `12-motherboards.md` | Motherboards | 10 (8 desktop, 2 server) |
| `13-ram.md` | Memory | 20 (16 desktop kits, 4 server RDIMMs) |
| `14-storage.md` | Storage | 17 (NVMe, SATA SSD, HDD, enterprise U.2) |
| `15-psus.md` | Power supplies | 13 (10 desktop ATX, 1 SFX, 2 server CRPS) |
| `16-coolers.md` | CPU coolers | 14 (air towers, a stock cooler, AIO liquid, server heatsinks) |
| `17-cases-fans.md` | Cases and fans | 14 (7 cases, 7 fan products) |
| `18-server.md` | Server add-ins and gear | 14 (NICs, HBA, chassis, switches, rack bits) |
| `19-boxes.md` | Retail boxes for all of the above | Run it **after** the others are merged |

To start one, give a cloud session on this repository the prompt *"Do the task in docs/tasks/catalog/<file>."*

**Setup and working rules are in `docs/tasks/README.md`. Read it first.** This file adds the catalogue rules.

## Brands
The game uses **fictional brands**: it will be sold, and real trademarks can't go on parts. Each brand stands in for
a real one, so model its look on the real brand's products. Never print the real names.

| Kind | Brand (game) | Looks like |
|---|---|---|
| CPU | **Arc** (existing) | AMD Ryzen |
| CPU | **Tiron** (existing) | Intel Core |
| CPU, server | **Arc Epoch** | AMD EPYC |
| CPU, server | **Tiron Platinum** | Intel Xeon |
| GPU chip | **Voltra RX** (existing) | AMD Radeon |
| GPU chip | **Verdia VTX** | NVIDIA GeForce RTX |
| GPU chip | **Tiron Lumen** | Intel Arc |
| Board/card partner | **Ridge** (existing) | ASRock |
| Board/card partner | **Aegis** | ASUS (ROG / TUF / Prime) |
| Board/card partner | **Mako** | MSI |
| Board/card partner | **Kestrel** | Gigabyte (AORUS / Eagle) |
| Board/card partner | **Zenith** | Zotac / Sapphire |
| RAM | **Volt** (existing) | generic |
| RAM | **Corvex** | Corsair |
| RAM | **G.Stride** | G.Skill |
| RAM | **Kingsland** | Kingston Fury |
| RAM | **Crux** | Crucial |
| RAM | **TeamForge** | TeamGroup |
| Storage | **Quill** (existing) | generic |
| Storage | **Sorin** | Samsung |
| Storage | **Westline** | WD |
| Storage | **Seacrest** | Seagate |
| Storage | Crux, Kingsland | |
| PSU | **Ampere** (existing) | generic |
| PSU | **Seastar** | Seasonic |
| PSU | **Hush** | be quiet! |
| PSU | Corvex, Mako, Aegis | |
| Cooler | **Frostpeak** (existing) | generic |
| Cooler | **Spinner** (existing stock) | AMD Wraith |
| Cooler | **Noctis** | Noctua (beige/brown, and chromax black) |
| Cooler | **Arctiq** | Arctic |
| Cooler | **Glacier** | DeepCool |
| Cooler | Hush, Corvex | |
| Case | **Brickhouse**, **Breeze** (existing) | |
| Case | **Lumin** | Lian Li |
| Case | **Facet** | Fractal |
| Case | **Nexa** | NZXT |
| Case | **Phanta** | Phanteks |
| Case | Hush, Corvex | |
| Fans | Noctis, Arctiq, Lumin, Corvex, Hush | |
| Server | **Strata** (existing servers) | Dell / HPE |
| Server | **Linkwave** (existing switch) | Cisco / Ubiquiti |
| Server | **Broadline** | Broadcom / LSI |
| Server | **Melnet** | NVIDIA Mellanox |
| Server | **Ampere** (existing UPS/PDU) | APC |

**Model names** keep the real numbering scheme; the numbers may match, as the game already does ("Arc 5 7600", "Tiron i5-14400"). Replace the brand and any trademarked series words:
- "Verdia VTX 5070 Ti 16 GB" is fine.
- "Mako Tomahawk" is not, because that's MSI's word. Invent "Mako Harpoon" instead.
- The same goes for "Vengeance", "Trident", "ROG", "AORUS", "Strix" and so on.

**Prices** are today's street prices of the real analog, in USD.

## Ids
- Lower case, prefixed by kind: `cpu_`, `gpu_`, `mb_`, `ram_`, `ssd_`, `hdd_`, `psu_`, `cooler_`, `case_`, `fan_`, `nic_`, `hba_`, `srv_`.
- Then the brand and the model, plus the variant where there are several. For example:
  - `gpu_verdia_5070ti_kestrel_white`
  - `ram_corvex_ddr5_32_white_rgb`
  - `hdd_seacrest_8tb`
- Never reuse an existing id (`Assets/Resources/Models/*.fbx`).

## Catalogue data: `docs/catalog/<family>.json`
The game will turn this file into shop entries, so fill it carefully. It is a JSON array, one object per part:

```json
{
  "id": "gpu_verdia_5070ti_kestrel_white",
  "model": "gpu_verdia_5070ti_kestrel_white",
  "brand": "Kestrel",
  "name": "Verdia VTX 5070 Ti Eagle-W 16 GB",
  "category": "GPU",
  "price": 799,
  "power_w": 300,
  "color": "#E8E8E6",
  "rgb": true,
  "analog": "Gigabyte RTX 5070 Ti Eagle Ice (docs only, never shown in game)",
  "desc": "One line for the shop.",
  "specs": { "vram_gb": 16, "length_mm": 304, "slots": 2.5, "fans": 3, "boost_mhz": 2588 },
  "game": { "gpu_connector": "Power16", "gpu_length": 0.304, "perf": 0 },
  "contract": "gpu",
  "new_contract": false
}
```

Field rules:
- **`category`** is one of Case, Motherboard, CPU, Cooler, RAM, GPU, PSU, Storage, Accessory, or a new one (Server, Network) for server gear.
- **`game`** holds the fields the game already has, using these names:
  - `socket`: V5 or L17;
  - `mem`: DDR4 or DDR5;
  - `ram_gb`, `per_box`, `storage_gb`, `sata25`;
  - `gpu_connector`: PCIe8x1, PCIe8x2 or Power16; `gpu_length` in metres;
  - `psu_watts`, `psu_efficiency`, `psu_eps8`, `psu_pcie8`, `psu_16`, `psu_sata`, `psu_modular`;
  - `cooler_max_w`;
  - `case_airflow`: 1.0 = average, lower is cooler;
  - `perf`: leave 0, the game balances it.
- **`contract`** names the contract the model follows.
- **`new_contract: true`** marks a part kind the game can't install yet (AIO, 3.5" HDD, server CPU socket, …). Document that new contract in your report.

## Contracts: what keeps the parts working in the game
- **Same kind as an existing part → same contract, exactly.** `docs/MODEL_PIPELINE.md` §2 has the frame and every anchor. A new V5 CPU has the cpu_arc5 package and anchors; a new GPU has the gpu_rx66 frame and anchor kinds; a new case has case_breeze's frame and anchor positions. Prove it with `Tools/Blender/anchor_compare.py` against the sibling, and put the table in your report.
- **Variation lives in the looks:** colours, logos, heatsink shapes, fan counts, RGB strips (`rgb` tag), labels, size along free axes (GPU length and height, RAM height, cooler height). Never in the anchors that install the part.
- **A new kind of part** (AIO cooler, 3.5" drive, server CPU, RDIMM, CRPS PSU, NIC, SFX PSU, case fan) gets a **new contract** that you design in the same style:
  - a frame;
  - anchors for every place it installs, plugs in, screws down or moves;
  - a section in your report written like `docs/MODEL_PIPELINE.md` §2, so the game can add support later.
- **Reuse the existing builders** (`build_cpu.py`, `build_gpu.py`, `build_board.py`, `build_ram.py`, `build_ssd.py`, `build_psu.py`, `build_cooler.py`, `build_case.py`, `parts_fan.py`, `build_datacenter.py`) with new configs, from your own new script.
  - **If you must add an optional hook to a builder your family owns** (listed in your task), re-export the existing parts it builds into a temp folder, prove them SAME with `extras_compare.py`, and don't commit those re-exports.
  - **Never edit** a builder another family owns, `dct_common.py`, `parts_pcb.py`, `parts_b.py`, `parts_c.py` or `parts_fan.py`.
- **Do not edit `README.md`** or anything in `docs/tasks/`, so the branches merge cleanly. Put your README line in your report.

## Each family task delivers
- `Tools/Blender/build_cat_<family>.py`, plus helper modules. It builds all your ids and takes `-- [ids] [--nopreview]`.
- The models, textures, previews and an anchor report `Logs/ModelPreviews/cat_<family>_report.txt`.
- `docs/catalog/<family>.json`.
- `docs/reports/cat_<family>.md`:
  - every model: id, triangles, contract and anchor comparison;
  - the new contracts;
  - deviations;
  - the rebuild command;
  - the README line.

**Work order:** do the most popular parts first. Commit and push after **every** model, so nothing is lost when tokens run out. If you run out of time, the report must say which ids are done and which are not.

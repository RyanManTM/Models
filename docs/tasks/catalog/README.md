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

## The unboxing on every part (required)
The game's unboxing works like real life. You peel the shipping tape, lift the retail box out, then open the box layer by layer: seals, flaps, foam, the clamshell or anti-static bag, then the part and its papers. Every part then still has its **protective films, caps and stickers** for the player to peel or pull off. Nothing vanishes; every piece goes in the bin by hand. See `docs/PACKAGING.md` for the box side.

**Every model you make must carry the anchors for its real protective bits.** The game builds the peel meshes itself from these anchors, and the cap models sit on the part.
- **A film** is an anchor `A_FILM_<NAME>_<n>`.
  - Its XY plane is the film surface and +Z faces out. `size` is the film area (w, h, thickness).
  - Meta `peel=<+x|-x|+y|-y>` gives the direction the player pulls from the tab corner. Add `tab=<corner>` too.
- **A cap or guard** is a small separate model that sits on the part (like `cap_pcie16`, `cap_dp`, `guard_ram_ddr5`).
  - Its local +Z is the pull-off direction.
  - Its `A_HIT_0` meta is `remove=+z,travel=<m>,blocks=install|plug|none`.
  - If yours needs a new cap model, make it in your script and list where it sits (parent anchor, position, rotation).
- **A sticker** (a warning or voltage sticker) is an `A_STICKER_<NAME>_<n>` anchor with `peel=`, plus a look mesh if it's printed.

| Part kind | Its protective bits (all of them, as on the real product) |
|---|---|
| GPU | `cap_pcie16` on the gold fingers (it sits at the GPU origin by contract), and `cap_dp` / `cap_hdmi` in every display port (they sit at the port anchors). `A_FILM_BACKPLATE_0`, `A_FILM_SHROUD_0`, and an `A_FILM_<NAME>_n` on every other glossy or RGB panel. A film disc on every fan hub sticker (`A_FILM_HUB_<n>`, in the `A_FAN_n` frame). An optional `A_CAP_POWER_0` over the power socket. Data-centre cards: films only. |
| Motherboard | The PnP socket cap (contract), `A_FILM_M2_0` on the M.2 heatsink pad, `A_FILM_IO_0`, `A_FILM_CHIPSET_0`, and an `A_FILM_<NAME>_n` on every other glossy cover or RGB shroud. Server boards: the socket covers. |
| RAM | `guard_ram_ddr5` / `guard_ram_ddr4` on the gold fingers (they sit at the RAM origin by contract). `A_FILM_SPREADER_0/1` on both sides of any heat spreader or RGB diffuser. RDIMMs: a new `guard_rdimm_ddr5` / `guard_rdimm_ddr4` for their notch. |
| CPU | Desktop: none on the part; the clamshell is in the box. Server: a clear contact cover `A_CAP_PADS_0` under the package, plus the carrier. |
| Cooler | `A_FILM_0` on the base or cold plate (contract), `A_FILM_TOP_0` on the top cover or pump cap, and `A_FILM_HUB_<n>` on every fan hub. Stock coolers: `cap_paste` on `A_PASTE_PRE_0`. AIO: `A_FILM_PUMP_0` on the pump cap or LCD, and a film on any glossy radiator end caps. |
| Fans | `A_FILM_HUB_0` on the hub sticker. RGB fans: also `A_FILM_RING_0` on a glossy frame. |
| Case | Films on **every glass panel, on both sides**: `A_FILM_GLASS_<n>`, in that panel's frame, so they ride with the moving panel. Films on glossy trims and the front panel, `A_FILM_<NAME>_n`. Hub films on the pre-installed fans. |
| PSU | The voltage warning sticker on `A_SWITCH_PSU_0` (`sticker_psu_voltage`), an `A_FILM_<NAME>_n` on glossy side panels or a display, and optional caps on modular ports `A_CAP_MOD_<n>`. CRPS: a film on the handle label. |
| SSD / HDD | SATA SSD: `A_FILM_LABEL_0`. NVMe with a heatsink: `A_FILM_<NAME>_0` on a glossy heatsink. U.2: a connector cap. HDD: none (it ships in an anti-static bag). |
| NIC / HBA | A dust plug in **every** SFP, SFP28 and QSFP cage (`cap_sfp` / `cap_qsfp` models at the cage port anchors, blocks=plug). A clear cap on the PCIe edge, sized to its x4, x8 or x16 length. |
| Rack gear | Films on glossy bezels and on LCDs or screens, `A_FILM_<NAME>_n`. A dust plug in every SFP/QSFP cage of switches. |

**List every film, cap and sticker in your report and in the catalogue JSON:**

```json
"unbox": {
  "films":    ["A_FILM_BACKPLATE_0", "A_FILM_SHROUD_0", "A_FILM_HUB_0", "A_FILM_HUB_1"],
  "caps":     [{"model": "cap_pcie16", "at": "origin", "blocks": "install"},
               {"model": "cap_dp", "at": "A_PORT_DP_0", "blocks": "plug"}],
  "stickers": []
}
```

**The papers in the box** come from the catalogue too.
- `"docs"` lists the kinds that come with the part: guide, manual, warranty, sticker (the case badge), driver, safety, quick-start.
- `"doc_notes"` gives 4–10 short real-sounding facts the game prints in them: install steps, connector tables, slot rules, specs, warnings.
- The motherboard manuals must state the real slot rules (which DIMM slots first) and the front-panel header pinout.

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

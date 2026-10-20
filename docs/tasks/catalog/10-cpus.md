# Catalogue 10: CPUs (14)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_cpus.py` (new) and optional hooks in `build_cpu.py`. If you add hooks, prove that `cpu_arc5`, `cpu_arc7`, `cpu_tiron5` and `cpu_arc9` re-export SAME.

**Delivers:** `docs/catalog/cpus.json` and `docs/reports/cat_cpus.md`.

## Desktop: existing contracts (10)
These must match their siblings' frame and every anchor exactly.
- **Socket V5** (the cpu_arc5 contract: 40 × 40 mm LGA package, octopus IHS):
  - Arc 3 8300G (4 cores, APU)
  - Arc 5 9600X (6 cores)
  - Arc 7 9700X (8 cores)
  - Arc 7 9800X3D (8 cores, 3D cache: a "3D V-CACHE"-style mark)
  - Arc 9 9950X3D (16 cores)
- **Socket L17** (the cpu_tiron5 contract: 37.5 × 45 mm, notched IHS):
  - Tiron i3-14100 (4 cores)
  - Tiron i5-14600K (14 cores)
  - Tiron i7-14700 (20 cores)
  - Tiron i7-14700K
  - Tiron i9-14900K (24 cores)
- **Each CPU gets its own IHS laser markings:** model, batch code, a 2D code and the pin-1 triangle. K and X parts may differ in markings only.
- **Game data:** `socket`, `power_w` (the real TDP/PPT), price.

## Server: new contracts (4)
These sockets are new, so design their contracts.
- **Arc Epoch**, on a new socket **SP-V**. The package is about 72 × 75 mm, an LGA with a large IHS. It ships in a bright orange plastic carrier frame that slides into the socket rail: the carrier is a separate moving piece on its own anchor.
  - Arc Epoch 9124 (16 cores)
  - Arc Epoch 9354 (32 cores)
  - Arc Epoch 9654 (96 cores)
- **Tiron Platinum 8480**, on a new socket **L46**. The package is about 61 × 105 mm, an LGA with a long IHS and its carrier clip.
- **The contract section** in your report covers:
  - the frame: origin at the bottom contact face centre, +Z up (like the desktop CPUs);
  - `A_MARK_PIN1_0`, `A_PASTE_0` and `A_HIT_0`;
  - the carrier anchor;
  - a note on what the socket needs.

# Catalogue 19: Retail and OEM boxes for the catalogue

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first, plus `docs/PACKAGING.md`.

**Run this after the family branches (10–18) are merged into `main`.** It boxes every part those families made.

**You own** `Tools/Blender/build_boxes.py`, `rig_common.py` and `rig_products.py`. Add a catalogue-driven path that reads `docs/catalog/*.json` to make the box items, rather than hand-writing 100 entries.

**Proof:** the existing 24 rigs (box_cpu_*, box_gpu_*, box_mb_*, box_ram_*, box_ssd_*, box_psu_*, box_cooler_*, box_case_*, box_usb_installer, box_cable_dp, box_fan_splitter) must re-export SAME with `extras_compare.py`. Don't commit those re-exports.

## For every consumer part (category CPU, GPU, Motherboard, RAM, Storage, PSU, Cooler, Case, and fans)
- **Make `box_<id>`** following the existing rig of the same kind (docs/PACKAGING.md §3): same opening sequence, inserts and papers.
  - CPU box: seals, tuck lid, tray, clamshell.
  - GPU box: sleeve, inner box, foam.
  - RAM box: tuck box with blister.
  - … and so on for each kind.
- **Printed art** is rendered from the part's own FBX, in the brand's style (the brand table in the catalogue README): colours, logo treatment, product shot, key specs, barcode.
- **Size:** the box is sized to its part. Put the size in the catalogue as `"box": "box_<id>"` and `"box_size": [x, y, z]`, so the game's `BoxSize` can use it.
- **New kinds need new rigs, designed in the same style:**
  - **AIO box:** the radiator and pump in a moulded pulp tray, tubes coiled, fans in a separate compartment.
  - **3.5" HDD:** a retail box or a brown bulk box with an anti-static bag.
  - **Fan packs:** a window box.
  - **SFX PSU:** a box with an SFX-to-ATX bracket.

## For server parts (CPUs, RDIMMs, CRPS PSUs, U.2, NICs, HBA, server boards, accelerators, rack gear)
- **Plain OEM packaging:** white or brown boxes with a printed label (part number, barcode, a "Strata"/brand sticker), inner foam and an anti-static bag.
  - One rig design per size class (small, card, board, PSU, 1U, 2U, 4U), scaled.
  - Server CPUs come in a clamshell tray, the carrier visible.

## Data and report
- Update each family's `docs/catalog/<family>.json` with `box` and `box_size`. Only add those two keys.
- Write the report `docs/reports/cat_boxes.md`.

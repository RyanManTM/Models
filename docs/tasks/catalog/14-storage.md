# Catalogue 14: Storage (17)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_storage.py` (new) and optional hooks in `build_ssd.py`. If you add hooks, prove that `ssd_1tb` and `ssd_sata_500` re-export SAME.

**Delivers:** `docs/catalog/storage.json` and `docs/reports/cat_storage.md`.

## M.2 2280 NVMe (the ssd_1tb contract) (8)
Each drive gets a real-looking label, its own controller/NAND layout, and single- or double-sided chips.

**Drives with their own heatsink** can't take the board's M.2 heatsink. Put `"has_heatsink": true` in specs and a note in the report; the heatsink must stay within a sane height (≤ 12 mm, Gen5 ≤ 25 mm).

1. Sorin 990 Pro-style 1 TB
2. Sorin 990 Pro-style 2 TB with its black RGB heatsink
3. Sorin 980-style 500 GB
4. Westline SN850X-style 2 TB
5. Westline SN850X-style 1 TB with heatsink
6. Westline SN580-style 1 TB
7. Crux P3 Plus-style 2 TB
8. Crux T705-style Gen5 2 TB with its tall finned heatsink

## 2.5" SATA SSD (the ssd_sata_500 contract) (3)
1. Sorin 870 EVO-style 1 TB
2. Crux MX500-style 2 TB
3. Kingsland A400-style 480 GB

## 3.5" hard drives (4, new contract)
- **Frame:** origin at the body centre, connectors on −x. Use the SATA data and power port anchors (`A_PORT_SATA_0`, `A_PORT_SATAPWR_0`), the side and bottom screw holes (`A_HOLE_n`), the label side up, and `A_HIT_0`.
- **The game** has only 2.5" mounts today, so note what a 3.5" bay needs.
- **Look:** the real look of the drive cover and its printed label, the PCB on the bottom.

1. Seacrest Barracuda-style 2 TB desktop
2. Westline Blue-style 4 TB
3. Seacrest IronWolf-style 8 TB NAS
4. Seacrest Exos-style 20 TB enterprise (helium, sealed top)

## Enterprise U.2 (2, new contract)
2.5", 15 mm thick, an SFF-8639 connector, and an aluminium enclosure with fins.
1. Sorin PM9A3-style 3.84 TB
2. Sorin 7.68 TB

# Catalogue 12: Motherboards (10)

Read `docs/tasks/README.md` (setup, rules) and `docs/tasks/catalog/README.md` (brands, ids, catalogue data, contracts) first.

**You own** `Tools/Blender/build_cat_boards.py` (new) and optional hooks in `build_board.py`.
- `build_board.py` doesn't rebuild identically even when unchanged (n-gon triangulation), so prove the existing boards with **anchors only** (`anchor_compare.py`).
- Follow how `build_parts_d.py` made `mb_ridge_x5` from the B5 layout: the `PremiumBoard` subclass.

**Delivers:** `docs/catalog/boards.json` and `docs/reports/cat_boards.md`.

**Each board** has its own I/O shield model `io_<board>`. Premium boards have the shield pre-attached in real life; still ship a separate shield model, and note pre-attached boards in the report.

## Desktop: existing contracts, all ATX (8)
Every anchor must be in the same place as the board's layout sibling (check with `anchor_compare.py`). The looks change: PCB colour, heatsink shapes and finishes, armoured slots, RGB zones, an I/O cover, a white or black theme, silkscreen. Brand looks follow the brand table.

**Socket V5 + DDR5** (the mb_ridge_b5 layout):
1. Aegis TUF-style B650: military tan and black.
2. Aegis ROG-style X870E: premium black with an RGB I/O cover.
3. Mako "Harpoon" B650: black and grey.
4. Kestrel Aero-style B650: white.

**Socket L17 + DDR5** (a new combination: the socket area and CPU anchors from mb_ridge_z4, the DIMM slots with their DDR5 notch from mb_ridge_b5; document it):
5. Aegis Prime-style Z790: white and silver.
6. Mako Edge-style Z790: white.
7. Kestrel AORUS-style Z790: black and orange accents.

**Socket L17 + DDR4** (the mb_ridge_z4 layout):
8. Ridge B760 DDR4: budget, black.

## Server (2, new contracts)
These go in servers, not in desktop cases.
1. **Strata SP-V board:** single-socket for Arc Epoch (socket SP-V, see the CPU task's contract), 12 DDR5 RDIMM slots, OCP NIC slot, 2 × M.2, BMC chip, SSI-EEB size.
2. **Strata L46 board:** dual-socket for Tiron Platinum, 16 DIMM slots.

The new contract sections cover: frame, sockets, DIMM slots, PCIe slots, power headers and mounting holes.

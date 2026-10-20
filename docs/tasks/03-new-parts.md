# Task 03: New parts to buy, with retail boxes

Read `docs/tasks/README.md` first: setup, rules, branches and the report.

Add four new parts to the catalog, each with its retail packaging rig. **They must drop into the game exactly like the existing parts of their kind**: the game installs parts through strict frame and anchor contracts (sockets, screws, cables).

- **Report:** `docs/reports/newparts.md`. Besides the usual, include:
  - an anchor-by-anchor comparison with each sibling part;
  - suggested catalog data for each new part: brand, name, key specs, price, power draw.
- **Budget:** within the existing parts' budgets (boards under about 50k triangles).
- You are the only task allowed to edit `build_boxes.py`, `rig_common.py` and `rig_products.py`.

## Read first
- `docs/MODEL_PIPELINE.md`: §2 is the per-part contract. Follow it to the letter.
- `docs/PACKAGING.md`: the box rig contract and per-product contents.
- The existing builders: `build_cpu.py`, `build_gpu.py`, `build_board.py`, `build_case.py`, `build_boxes.py`, `rig_common.py`, `rig_products.py`.
- Their reports in `Logs/ModelPreviews/`: `parts_a_report.txt`, `parts_b_report.txt`, `case_breeze_report.txt`, `box_*_report.txt`.

## How to build without breaking anything
- **Put each new part in a new script** (e.g. `Tools/Blender/build_parts_d.py`). Reuse the existing builder functions and classes with a new config or style rather than copying them.
- **If you must touch an existing builder** to make it configurable, re-export the existing parts it builds into a temp folder. Then prove they are unchanged with `Tools/Blender/extras_compare.py` (it prints SAME / ONLY ADDED / CHANGED) and don't commit the re-exports.
- **Exception:** `build_board.py` doesn't rebuild identically even unchanged (n-gon triangulation), so for the board compare anchors only.

## Models, in this order
1. **`cpu_arc9`**: a high-end Socket V5 CPU ("ARC 9 9900X").
   - The **same package size, frame and anchors** as cpu_arc5 and cpu_arc7, so it fits the same socket; check `parts_a_report.txt`.
   - Its own heat-spreader markings, and the same octopus IHS.
2. **`gpu_rx77`**: an upper-mid card between rx66 and rx88: 2.5-slot, 3 fans, about 0.27 m long, two PCIe 8-pin power ports.
   - The **same frame and anchor kinds** as gpu_rx66/rx88:
     - the PCIe edge at the origin and the bracket at x +0.095;
     - `A_PORT_DP_0..2` and `A_PORT_HDMI_0` at the same bracket positions;
     - the screw anchors, `A_FAN_n` with hub stickers, `A_FILM_BACKPLATE_0` and `A_FILM_SHROUD_0`;
     - power port anchors like rx66's PCIe 8-pin, but two of them.
   - Its own distinct shroud design (for example dark grey with silver accents).
3. **`case_aero`**: a third mid-tower with exactly the case contract:
   - frame 0.42 × 0.45 × 0.21, origin at the bottom centre, −x front, window +z;
   - the **same anchor names and positions** as `case_breeze` (see `case_breeze_report.txt`): board socket, standoffs (and which are `pre=1`), PSU socket, I/O shield, slot covers with screws, side and back panels with thumbscrews, front I/O, fans and fan plugs, front-panel plugs, grommets, SSD mounts.
   - The look changes: black, a "panoramic" glass front corner plus glass side, three bottom intake fans with ARGB.
   - Reuse `build_case.py`'s builder with a new style.
4. **`mb_ridge_x5`** plus its I/O shield **`io_ridge_x5`**: a premium ATX Socket V5 DDR5 board.
   - It has **exactly the layout contract of mb_ridge_b5**: every anchor at the same position, the same hole positions, socket, RAM slots, PCIe slots, M.2 slot, headers and rear I/O. Then the game's cases, standoffs and cables work unchanged.
   - It looks premium: white or silver theme, bigger VRM heatsinks, armoured slots, a white I/O cover.
   - Reuse `build_board.py`'s Board class with a new config.
5. **Retail box rigs** `box_cpu_arc9`, `box_gpu_rx77`, `box_case_aero` and `box_mb_ridge_x5`:
   - Add entries to `build_boxes.py` / `rig_products.py`, following each existing product of the same kind (same opening sequence and contents per docs/PACKAGING.md §3).
   - The printed art is rendered from the new part FBX.
   - Keep the box sizes of the sibling products.
   - Then prove the existing 20 rigs are unchanged (extras_compare.py on a temp re-export; don't commit those re-exports).

# Task 02: Small parts and packaging contents

Read `docs/tasks/README.md` first: setup, rules, branches and the report.

These are the small parts the game still draws with plain code. Write a new script `Tools/Blender/build_smallparts.py`, plus helpers if you want. It takes `-- [ids] [--nopreview]`.
- Report: `docs/reports/smallparts.md`.
- Budget: under about 8k triangles each (`bundle_modular` up to about 15k).
- In the report, include which packaging anchor each model fits, with its margins.

## Read first
- `docs/PACKAGING.md`: the packaging rig contract. **Flat items** (`A_ITEM_CORD`, `A_ITEM_POUCH`, `A_ITEM_PART` with `frame=flat`) are placed with the anchor at the centre of the face they rest on: +Z out of their top face, +Y the top edge of their print, size (w, h, t), occupying z 0..t.
- `Tools/Blender/build_plugs.py` and `Logs/ModelPreviews/plug_*_report.txt`: the existing plug heads (plug_dp, plug_c13, plug_sata_data, plug_fan4 and so on). Reuse their look.
- `Tools/Blender/shipping_bits.py`: `twist_tie`, `velcro_strap`, `hw_bag`.
- These box reports, for the space each coil must fit (all in `Logs/ModelPreviews/`):
  - `box_psu_450_report.txt`, `box_psu_750_report.txt` (`A_ITEM_CORD_0`, `A_ITEM_POUCH_0`);
  - `box_mb_ridge_b5_report.txt` (`A_ITEM_CORD_0`, kind=sata);
  - `box_cable_dp_report.txt`, `box_fan_splitter_report.txt` (`A_ITEM_PART_0`, frame=flat).

## Models
All coils and bundles are **look items** (the game draws working cables itself). Each is a flat item: origin at the bottom centre, lying flat, +Y up, with `A_HIT_0`, sized to fit its packaging anchor space.

1. **`coil_dp`**: a 1.8 m black DisplayPort cable coiled in neat loops (about 0.12 m across), with both DP plug heads (latch buttons, gold contacts) and a white twist tie. Fits box_cable_dp's `A_ITEM_PART_0`.
2. **`coil_c13`**: a 1.5 m black PSU power cord, coiled with a twist tie: a C13 end and a NEMA 5-15 wall plug. Fits the PSU boxes' `A_ITEM_CORD_0`.
3. **`coil_sata_pair`**: two flat SATA data cables (one with a right-angle end, latches on the connectors) bundled with a twist tie. Fits the motherboard box's `A_ITEM_CORD_0`.
4. **`bundle_modular`**: the 750 W PSU's modular cable set, folded and held by two black velcro straps. It contains:
   - a 24-pin ATX cable;
   - 2 × EPS 8-pin;
   - 2 × PCIe 8-pin;
   - 1 × 12V-2x6;
   - 2 × SATA power chains.
   Use sleeved black cables with realistic connector heads. Fits `A_ITEM_POUCH_0` / the existing `cable_pouch` model.
5. **`coil_fan_splitter`**: a 4-pin PWM 1-to-2 fan splitter (about 10 cm: one male input, two female outputs), folded for its bag. Fits box_fan_splitter's `A_ITEM_PART_0`.
6. **`syringe_paste`**: a thermal paste syringe (grey compound visible through the barrel, plunger, cap, a printed label "FROSTPEAK thermal compound 1.5 g"). About 0.09 m long. Flat item.
7. **`standoff_bag`**: replaces a bag the game builds in code today. It must match that code's layout exactly:
   - **The bag:** a clear zip bag 0.084 (x) × 0.009 (y) × 0.060 (z), origin at its bottom centre, lying flat. Use `bag_clear`, slightly pillowy, with heat-sealed edges.
   - **The zip strip** runs along the +z edge at z = 0.0265.
   - **The label:** a printed white label "M3 BRASS STANDOFFS", centred at (0.021, top surface, −0.012), about 0.034 × 0.02.
   - **Model only the bag.** The game spawns the brass standoffs and screws inside, so add anchors for where they lie:
     - `A_ITEM_0..3` at (−0.03 + i × 0.0105, 0.0033, −0.006 + (i % 2) × 0.006), rotated about +Y by 90° + ((i % 3) − 1) × 16°;
     - `A_SCREW_0..2` at (0.012 + i × 0.009, 0.0028, 0.009);
     - `A_HIT_0`: size 0.084 × 0.011 × 0.06, at y 0.0045.
8. **`fan4_female`** and **`fan3_female`**: female 4-pin and 3-pin fan connector housings, the kind on the splitter outputs and on fan extension cables.
   - **Frame:** the contact (socket) face at the origin, +Z back along the wire, +Y = the side with the polarising ramp.
   - **Geometry:** sockets at 2.54 mm pitch. The 4-pin is about 0.0105 × 0.0055 × 0.0075; the 3-pin is narrower.
   - **Wires:** short wire stubs out of the back, like the plug models.

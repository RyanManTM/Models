# Task 02 report: small parts and packaging contents

Script: `Tools/Blender/build_smallparts.py` (no helpers; it reuses `build_plugs.py` for the plug heads, `parts_c.py`,
`parts_b.py`, `shipping_lib.py` and `shipping_bits.py`, and changes none of them).

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_smallparts.py -- [ids...] [--nopreview]
```

No ids = all of them. Each model writes `Assets/Resources/Models/<id>.fbx`, its textures, previews
`Logs/ModelPreviews/<id>_0..1.png` (Workbench) and `<id>_2..3.png` (Cycles), and `Logs/ModelPreviews/<id>_report.txt`.

README line for the script table:

| `build_smallparts.py` | Box contents: coils `coil_dp/c13/sata_pair/fan_splitter`, `bundle_modular`, `syringe_paste`, `standoff_bag`, fan connector housings `fan4_female/fan3_female` |

## Frames

**Flat items** (every coil, the bundle, the syringe, the standoff bag) follow `docs/PACKAGING.md`:
- origin at the bottom centre, lying flat on y = 0, +Y up;
- width along x, height along z, the top edge of the print (and of the item) towards **−z**.

Every box anchor for these items (`A_ITEM_CORD_0`, `A_ITEM_POUCH_0`, `A_ITEM_PART_0` with `frame=flat`) has local
+Z up and local +Y towards −z, so the model placed at the anchor with identity rotation maps x → w, −z → h,
+y → t. The margins below are anchor size minus model size (positive = room to spare).

**Removable ties.** Each coil's twist tie (and the bundle's velcro straps) is a moving piece on `A_TIE_<n>`
(`tie=twist` or `tie=velcro`) so the code can take it off. The anchor sits on top of the bundle, +Z up, +Y along
the bundle.

## Models

### coil_dp
- 1.8 m black DisplayPort cable (5.8 mm, the plug model's cable) coiled in 6 turns, about 0.11 m across. Both DP heads
  (the `plug_dp` look: latch button, gold contacts, hooks) are tucked inside the coil, and a white twist tie holds the
  bundle where the leads join.
- Size 0.1080 (x) × 0.0138 (y) × 0.1103 (z) m; **7416 triangles**, 7 meshes.
- Anchors:
  - `A_HIT_0` pos (0, 0.0069, 0), size 0.1080 × 0.0138 × 0.1103.
  - `A_TIE_0` pos (−0.0280, 0.0113, −0.0349), fwd +y, size 0.0237 × 0.0162 × 0.0159, meta `tie=twist,colour=white`;
    piece `tie_0@A_TIE_0#white_plastic`.
- Fits `box_cable_dp` `A_ITEM_PART_0` (0.115 × 0.115 × 0.020): margins w +0.0070, h +0.0047, t +0.0062.

### coil_c13
- 1.5 m black PSU power cord (18/3 SVT, 6.0 mm) coiled in 4.5 turns with a white twist tie. Inside the coil:
  - the C13 end (the `plug_c13` look), lying flat;
  - a new NEMA 5-15P wall plug, lying on its side: slim moulded body with grip ribs, two 1.5 mm blades with their
    holes, the round ground pin, a ribbed strain relief.
- Size 0.1100 (x) × 0.0188 (y) × 0.0878 (z) m; **6532 triangles**, 4 meshes.
- Anchors:
  - `A_HIT_0` pos (0, 0.0095, 0), size 0.1100 × 0.0188 × 0.0878.
  - `A_TIE_0` pos (−0.0149, 0.0111, −0.0336), fwd +y, size 0.0218 × 0.0162 × 0.0163, meta `tie=twist,colour=white`;
    piece `tie_0@A_TIE_0#white_plastic`.
- Space:
  - `box_psu_750` `A_ITEM_CORD_0` (0.120 × 0.090 × 0.016): margins w +0.0100, h +0.0022, **t −0.0028**.
  - `box_psu_450` `A_ITEM_CORD_0` (0.090 × 0.075 × 0.014): margins **w −0.0200, h −0.0128, t −0.0048**.
  - See the deviations below.

### coil_sata_pair
- Two black flat SATA data cables, about 0.5 m each (7.6 × 1.4 mm flat cable), each folded in five layers. They lie
  side by side, held by a white twist tie round the middle.
  - Each cable's first plug (the `plug_sata_data` look, with the steel latch clip) lies past the −x end.
  - Its last plug lies beside the bundle, the cable curling back from the top layer. The cable rolls up on its edge
    for that U-turn, as a real flat cable does.
  - Cable 2 ends in a new right-angle plug: the same face and latch, the cable leaving a ribbed boot on its side.
- Size 0.1178 (x) × 0.0119 (y) × 0.0429 (z) m; **6328 triangles**, 5 meshes.
- Anchors:
  - `A_HIT_0` pos (0, 0.0060, 0), size 0.1178 × 0.0119 × 0.0429.
  - `A_TIE_0` pos (−0.0034, 0.0090, −0.0015), fwd +y, up +x, size 0.0248 × 0.0162 × 0.0142, meta
    `tie=twist,colour=white`; piece `tie_0@A_TIE_0#white_plastic`.
- Fits `box_mb_ridge_b5` and `box_mb_ridge_z4` `A_ITEM_CORD_0` (0.120 × 0.075 × 0.012): margins w +0.0022,
  h +0.0321, t +0.0001.

## Deviations

- **coil_c13 is bigger than the PSU boxes' cord spaces.** The plug heads set the thickness:
  - The NEMA 5-15P pin pattern needs a body at least about 17 mm across the blades.
  - The C13 head is 17 mm thick.
  - The loops are 11–14 mm thick (two layers of 6 mm cord, plus the tie).
  - In the 450's space (0.090 × 0.075 × 0.014), 1.5 m of 6 mm cord plus two heads doesn't fit at all by volume
    (cord alone ≈ 57 cm³ coiled, heads ≈ 45 cm³, space 94 cm³). So the model fits the 750's footprint instead.
  - Suggested change on the Unity/rig side: give both PSU boxes `A_ITEM_CORD_0` at least **0.115 × 0.090 × 0.019**.
    The 450's rig has room on top of the PSU: x ±0.06 is free beside the screw bag, and there is about 4 mm above the
    safety sheet, so the papers would need to move up about 5 mm. The 750's cord stands in the +x compartment; t
    there is the compartment width.
  - Or let the code scale the coil to the anchor: × 0.74 in y for the 450's t.

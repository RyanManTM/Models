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
- Size 0.1079 (x) × 0.0138 (y) × 0.1103 (z) m; **7416 triangles**, 7 meshes.
- Anchors:
  - `A_HIT_0` pos (0, 0.0069, 0), size 0.1079 × 0.0138 × 0.1103.
  - `A_TIE_0` pos (−0.0280, 0.0113, −0.0349), fwd +y, size 0.0237 × 0.0162 × 0.0159, meta `tie=twist,colour=white`;
    piece `tie_0@A_TIE_0#white_plastic`.
- Fits `box_cable_dp` `A_ITEM_PART_0` (0.115 × 0.115 × 0.020): margins w +0.0071, h +0.0047, t +0.0062.

## Deviations

None so far.

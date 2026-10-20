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

### coil_fan_splitter
- A 4-pin PWM 1-to-2 fan splitter in black braided sleeving (3.6 mm), about 0.1 m from the input to each output,
  folded for its bag.
  - The input (the `plug_fan4` look, sockets: it goes onto the board header) and the two receiving outputs (the
    `fan4_female` housing) lie side by side at the +z end, all three pointing +z.
  - The second output has no tach pin: only one fan reports its speed, as on real splitters.
  - Heat shrink on each connector and on the Y junction. The two branches loop back over the top from the
    junction. A white twist tie holds the three sleeves together.
- Size 0.0356 (x) × 0.0073 (y) × 0.0713 (z) m; **4536 triangles**, 6 meshes.
- Anchors:
  - `A_HIT_0` pos (0, 0.0037, 0), size 0.0356 × 0.0073 × 0.0713.
  - `A_TIE_0` pos (0, 0.0048, 0.0016), fwd +y, up +z, size 0.0180 × 0.0162 × 0.0100, meta `tie=twist,colour=white`;
    piece `tie_0@A_TIE_0#white_plastic`.
- Fits `box_fan_splitter` `A_ITEM_PART_0` (0.070 × 0.080 × 0.012): margins w +0.0344, h +0.0087, t +0.0047.

### syringe_paste
- A 1.5 g thermal paste syringe lying flat, 0.086 m long.
  - A clear barrel (7.2 mm) with the grey paste showing in its front part and in the nozzle.
  - The nozzle under a ribbed grey cap.
  - A black rubber stopper and a white X-ribbed plunger with its thumb pad, and the finger flange.
  - A wrap-round printed label (`tex_smallparts_syringe_label`): "FROSTPEAK", "THERMAL COMPOUND", "1.5 g",
    "8.5 W/mK", a mountain logo, small print and a lot number.
- The tip points −z: the top edge as a flat item, or tip up when it stands in a box. The label text runs along the
  barrel, reading from the plunger to the tip.
- Size 0.0120 (x) × 0.0073 (y) × 0.0860 (z) m; **2132 triangles**, 6 meshes.
- Anchors:
  - `A_HIT_0` pos (0, 0.0036, 0), size 0.0120 × 0.0073 × 0.0860.
  - `A_CAP_0` pos (0, 0.0036, −0.0298), fwd −z, meta `pull=-z,dist=0.015`: the cap, piece
    `cap_0@A_CAP_0#grey_plastic`.
  - `A_PLUNGER_0` pos (0, 0.0036, 0.0430), fwd +z (the thumb's side), meta `slide=-z,dist=0.021`: the plunger,
    pieces `plunger_0@A_PLUNGER_0#white_plastic` and `#rubber`.
  - `A_TIP_0` pos (0, 0.0036, −0.0393), fwd −z (where the paste comes out), meta `paste=1.5g`.
- Space: no anchor was named in the brief. The tower cooler box's look-only syringe anchor `A_ITEM_HW_1`
  (`kind=syringe`, 0.012 × 0.075 × 0.009, length along h) gives margins w 0.0000, **h −0.0110**, t +0.0017. The
  brief asks for about 0.09 m; the box's look syringe is 0.075.

### standoff_bag
- The case's standoff bag, on the layout of the code that builds it today: a clear zip bag 0.084 (x) × 0.009 (y) ×
  0.060 (z), origin at its bottom centre, lying flat.
  - `bag_clear` throughout.
  - A pillowy top film draped over the contents with a millimetre of slack.
  - Heat seals (with their fine ribbing) on the −x, +x and −z sides.
  - The press-seal zip (two tracks) along the +z edge at z = 0.0265, and the lip above it.
  - The printed white label "M3 BRASS / STANDOFFS" (`tex_smallparts_standoff_label`, with a hex icon and
    "4 × STANDOFF + 3 × SCREW"), 0.034 × 0.020, centred at (0.021, top surface, −0.012).
  - The label's text has its top towards the zip (+z), as on a real zip bag.
- **Only the bag**: the game spawns the standoffs and screws at the anchors. The previews show copies of
  `standoff_brass` and `screw_ph2` placed there to check the fit; they are not in the FBX.
- Size 0.0840 (x) × 0.0069 (y, film top; the hitbox is 0.011) × 0.0600 (z) m; **3146 triangles**, 2 meshes.
- Anchors (exactly as the brief):
  - `A_HIT_0` pos (0, 0.0045, 0), size 0.084 × 0.011 × 0.06.
  - `A_ITEM_0..3` pos (−0.03 + i × 0.0105, 0.0033, −0.006 + (i % 2) × 0.006). Each is rotated about +Y by
    90° + ((i % 3) − 1) × 16°, so fwd = (sin, 0, cos) of that angle: (0.961, 0, 0.276), (1, 0, 0),
    (0.961, 0, −0.276), (0.961, 0, 0.276). Meta `kind=standoff_brass`; the standoff's own frame goes there, lying
    on its side.
  - `A_SCREW_0..2` pos (0.012 + i × 0.009, 0.0028, 0.009), identity rotation, meta `kind=screw_ph2`.
  - Added: `A_ZIP_0` pos (0, 0.0016, 0.0265), size 0.084 × 0.004 × 0.006, meta `zip=x,press=1`: the zip, for the
    code to open the bag.
- Fits its own spec: the film tops out at 0.0071 (under the 0.009 bag height). It clears every spawned item by at
  least 0.6 mm.

### fan4_female and fan3_female
- The receiving housings on the splitter outputs and on fan extension cables: the end a fan's own plug
  (`plug_fan4` / `plug_fan3`) slides onto.
  - A housing with crimp windows underneath and a pin-1 nick on top.
  - Gold square pins at 2.54 mm standing 5.8 mm in front of the contact face, as on a board header.
  - The polarising wall with its friction ramp along the +Y side. It covers pins 1–3; the 4-pin's PWM pin stays
    outside it, so a 3-pin plug fits too.
  - Short wire stubs out of the back, like the plug models.
  - fan4_female: black housing, black wires. fan3_female: white housing, black / red / yellow wires (as `plug_fan3`).
- **Frame:** origin at the centre of the contact face (where the fan plug's face seats). +Z runs back along the
  wires, +Y is the ramp side. The housing occupies z 0..0.0075, the pins and wall z −0.0058..0. Pin 1 (GND) is at +x.
- Housing size: fan4_female 0.0106 × 0.0055 × 0.0075, fan3_female 0.0079 × 0.0055 × 0.0075 (W × H × L).
  - Overall with pins and wire stubs: x ±0.0053 / ±0.0040, y −0.0027..0.0030, z −0.0060..0.0335.
- **536 / 468 triangles**, 3 / 4 meshes.
- Anchors (the same on both, numbers for the 4-pin):
  - `A_HIT_0` pos (0, 0.0003, 0.0009), size 0.0126 × 0.0075 × 0.0143.
  - `A_CABLE_0` pos (0, −0.0002, 0.0335), fwd +z, meta `r=0.0025,n=4`: the wire stubs' end.
  - `A_PORT_FAN_0` pos (0, −0.0002, −0.0058) at the pin tips, **fwd −z** (where the fan plug comes from), size
    0.0126 × 0.0065 × 0.008.
    - Meta in the board headers' format: `depth=0.0058,pins=4;pin1=-0.00381,0.00000;colstep=0.00254,0.00000;pinout=GND|12V|SENSE|PWM`
      (3-pin: `pins=3;pin1=-0.00254,…;pinout=GND|12V|SENSE`).
    - pin1 and colstep are in the anchor's own axes, as on the board's `A_PORT_FAN*`.

## Deviations

- **The fan connector naming.** The brief calls the splitter's input "male" and its outputs "female". These models
  follow that: `fan4_female` / `fan3_female` are the receiving ends a fan plugs into, with pins and the polarising
  wall. The splitter's input end is the existing `plug_fan4` look (sockets), which goes onto the board header. In
  connector-maker terms the contacts are the other way round (the receiving end carries the male pins).

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

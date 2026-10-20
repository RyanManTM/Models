# Catalogue 16: CPU coolers

Branch `claude/cat-coolers`. Script `Tools/Blender/build_cat_coolers.py` (new; it imports `build_cooler.py`'s
`spring_screw` and `box` and wraps `parts_fan.make_fan`; no existing builder was edited). Catalogue data:
`docs/catalog/coolers.json`. Anchor report: `Logs/ModelPreviews/cat_coolers_report.txt`.

## Status

| # | id | contract | status |
|---|---|---|---|
| 1 | `cooler_arctiq_34_black` | cooler_tower | done |
| 2 | `cooler_arctiq_34_white` | cooler_tower | done |
| 3 | `cooler_glacier_ak400_white` | cooler_tower | done |
| 4 | `cooler_glacier_ak620_black` | cooler_tower | done |
| 5 | `cooler_noctis_d15` | cooler_tower | done |
| 6 | `cooler_noctis_d15_black` | cooler_tower | done |
| 7 | `cooler_noctis_l9` | cooler_tower | done |
| 8 | `cooler_frostpeak_120_rgb` | cooler_tower | done |
| 9 | `cooler_tiron_stock` | cooler_stock | done |
| 10 | `cooler_arctiq_lc240` | AIO (new) | done |
| 11 | `cooler_corvex_h150i_white` | AIO (new) | done |
| 12 | `cooler_glacier_ls720` | AIO (new) | done |
| 13 | `cooler_srv_epoch_1u` | server heatsink SP-V (new) | done |
| 14 | `cooler_srv_platinum_2u` | server heatsink L46 (new) | done |

## Models

| id | tris | height | contract | anchors vs sibling |
|---|---|---|---|---|
| `cooler_arctiq_34_black` | 36 672 | 157 mm | cooler_tower | vs `cooler_tower`: SAME 7, DIFF 4 (fan, hitboxes, top film: the free axes) |
| `cooler_arctiq_34_white` | 36 672 | 157 mm | cooler_tower | as the black one |
| `cooler_glacier_ak400_white` | 42 092 | 155 mm | cooler_tower | SAME 7, DIFF 4 (fan, hitboxes, top film) |
| `cooler_glacier_ak620_black` | 67 548 | 160 mm | cooler_tower | SAME 6, DIFF 5, ONLY_B 4 (A_FAN_1, A_PLUG_FAN_1, A_HIT_3..4) |
| `cooler_noctis_d15` | 57 438 | 165 mm | cooler_tower | SAME 6, DIFF 5, ONLY_B 4 (as AK620) |
| `cooler_noctis_d15_black` | 57 438 | 165 mm | cooler_tower | SAME 6, DIFF 5, ONLY_B 4 (as AK620) |
| `cooler_noctis_l9` | 24 346 | 37 mm | cooler_tower (low profile) | SAME 6, DIFF 5 (fan faces +z on top; top film on the fan hub) |
| `cooler_frostpeak_120_rgb` | 38 396 | 158 mm | cooler_tower | SAME 7, DIFF 4, ONLY_B 1 (A_PLUG_ARGB_0) |
| `cooler_arctiq_lc240` | 33 570 | pump 53 mm, rad 288 x 121 x 38 | aio (new) | pump base: screws and A_FILM_0 SAME as cooler_tower |
| `cooler_corvex_h150i_white` | 49 678 | pump 54 mm, rad 408 x 121 x 27 | aio (new) | as above, plus A_SCREEN_0 |
| `cooler_glacier_ls720` | 49 014 | pump 52 mm, rad 408 x 121 x 27 | aio (new) | as above |
| `cooler_srv_epoch_1u` | 9 286 | 27 mm (1U) | heatsink_spv (new) | new socket, no sibling |
| `cooler_srv_platinum_2u` | 25 910 | 67 mm (2U) | heatsink_l46 (new) | new socket, no sibling |
| `cooler_tiron_stock` | 21 550 | 53 mm | cooler_stock | vs `cooler_stock`: SAME 9 of 9 (every anchor) |

### Anchor comparison (anchor_compare.py, `cooler_tower` = A)

`cooler_arctiq_34_black` (the white one is identical):

| anchor | result | A pos | B pos |
|---|---|---|---|
| `A_FAN_0` | DIFF pos d=0.0010; meta rpm=1800 -> rpm=2100 | (-0.0385, 0.0000, 0.0950) | (-0.0380, 0.0000, 0.0958) |
| `A_FILM_0` | SAME | (0.0000, 0.0000, 0.0000) | (0.0000, 0.0000, 0.0000) |
| `A_FILM_TOP_0` | DIFF pos d=0.0022; size 0.040,0.115 -> 0.039,0.114 | (0.0005, 0.0000, 0.1549) | (0.0005, 0.0000, 0.1571) |
| `A_HIT_0` | DIFF pos d=0.0008; size | (0.0000, 0.0000, 0.0974) | (0.0000, 0.0000, 0.0983) |
| `A_HIT_1` | DIFF pos d=0.0010 | (-0.0385, 0.0000, 0.0950) | (-0.0380, 0.0000, 0.0958) |
| `A_HIT_2` | SAME | (0.0000, 0.0000, 0.0120) | (0.0000, 0.0000, 0.0120) |
| `A_PLUG_FAN_0` | SAME | (-0.0340, 0.0900, 0.0060) | (-0.0340, 0.0900, 0.0060) |
| `A_SCREW_PH2_0..3` | SAME | (+-0.0330, +-0.0330, 0.0214) | (+-0.0330, +-0.0330, 0.0214) |

On the dual towers the second stack shifts the hitbox numbering (`A_HIT_2` is the second stack, not the base), so
`A_HIT_2` is a DIFF there and the base hitbox is the last `A_HIT_n`. In every comparison `A_SCREW_PH2_0..3` and
`A_FILM_0` are SAME and `A_PLUG_FAN_0` is SAME.

The installing anchors (the four spring screws and the base film) are SAME on every tower; only the free axes
(height, fan position and speed, hitboxes, the top film) differ.

## The cooler_tower contract as used here

- Frame: origin at the centre of the base contact face, +z away from the board, x towards the rear I/O (air flows
  -x -> +x), y towards the board's top edge.
- `A_SCREW_PH2_0..3` (spring screws on the X bracket at (+-0.033, +-0.033), head at z 0.0214), `A_FILM_0` (base
  film, moving piece): byte-for-byte cooler_tower's geometry and anchors.
- `A_FAN_n`: the fan rotors (meta `axis=z,spin=-1,rpm=..`, plus `rgb=1` on ARGB fans). Fan 0 is the front fan.
- `A_PLUG_FAN_n`: each fan's loose 4-pin plug. Fan 0's meta says `target=CPU_FAN`; a second fan's says
  `target=SYS_FAN` (CPU_OPT on real boards; the game can also chain it with a splitter).
- `A_PLUG_ARGB_n` (ARGB coolers): the 5 V 3-pin ARGB plug (meta `kind=argb3,target=ARGB`, the board's
  `A_PORT_RGB_0`). The Frostpeak's top-cap ring is daisy-chained into the fan's lead, so it has one plug.
- `A_FILM_TOP_0`: the clear film on the label cover (anchor only).
- `A_HIT_n`: one per fin stack, one per fan, then the base.
- Total height <= 165 mm (the specs give each one's height).

## New contract: AIO liquid cooler (`aio`)

Ids `cooler_arctiq_lc240`, `cooler_corvex_h150i_white`, `cooler_glacier_ls720`.

**Pump block (static, the model root):** the cooler_tower frame and base contract: origin at the centre of the
cold plate's contact face, +z away from the board, x towards the rear I/O, y towards the board's top edge.
- `A_SCREW_PH2_0..3`: the four spring screws on the X bracket, same poses and meta as cooler_tower
  ((+-0.033, +-0.033, 0.0214), `spring=1,thread=M3,turns=8`).
- `A_FILM_0`: the base film (moving piece), same as cooler_tower.
- `A_FILM_TOP_0`: the clear film on the pump cap (meta `on=pump_cap`).
- `A_PLUG_FAN_0`: the pump's loose 4-pin plug, at cooler_tower's pose; meta `target=AIO_PUMP` (CPU_FAN works too).
  RGB pumps also have `A_PLUG_ARGB_0` (5 V 3-pin, `target=ARGB`; the fans' RGB is chained into the pump).
- `A_SCREEN_0` (Corvex only): the round LCD, forward +z, meta `kind=lcd,shape=round,res=480x480,diameter=0.048`.
  The game draws the screen onto it; the shipped texture shows an idle coolant-temperature face.
- `A_HIT_0`: the pump body.

**Tubes:** `A_TUBE_0` and `A_TUBE_1` sit at the pump's swivel fittings (on the pump's -x side), forward = the
direction the tube leaves (-x), up +z. Each carries a moving piece `tube@A_TUBE_n`: 8 straight-swept segments with
ferrule rings at the joints, modelled in the shipped pose (the radiator lying beside the pump). Meta:
`to=A_PORT_RAD_n@A_RAD_0,radius=0.0055,segments=8,min_bend=0.035,max_length=<real tube length>,length=<as modelled>`.

**How the game should route them:** once the radiator is placed, rebuild each tube as a swept circle (radius
0.0055) along a cubic Bezier from `A_TUBE_n` to `A_PORT_RAD_n@A_RAD_0`: P0 = A_TUBE_n, P1 = P0 + its forward x 0.06,
P3 = the port, P2 = P3 + the port's forward x 0.06 (the tube enters the port against the port's forward). Split it
into the 8 segments (or bend the 8 shipped segments along the curve), and refuse a placement whose curve would be
longer than `max_length` or bend tighter than `min_bend`. The two tubes run side by side 0.02 m apart.

**Radiator (moving piece `A_RAD_0`):** origin at the core centre; local +Z = the fan side, local +X = along the
length (the port tank at -X), local +Y = across. Size = the whole radiator. Meta
`fans=<n>,size=120,length=<m>,thickness=<m>,fan_side=+z,ports=-x`. In the model it lies flat beside the pump
(centre (0, -0.20, T/2)), fans up. Everything below belongs to it (flat export, linked by name):
- `rad@A_RAD_0#...`, `radlabel@A_RAD_0#...` and the fan frames `radfan<k>_*@A_RAD_0#...`: its meshes.
- `A_RAD_FAN_k@A_RAD_0`: the fan rotors (`radfan<k>_rotor@A_RAD_FAN_k@A_RAD_0`), forward = +Z (away from the core),
  meta as a case fan (`axis=z,spin=-1,rpm=..`, `rgb=1` on RGB fans). Fan k sits at local x = (k - (n-1)/2) x 0.120.
- `A_HOLE_RAD_i@A_RAD_0`: the case-side screw holes (4 per fan, at +-0.0525 round each fan centre, on the -Z face),
  forward -Z, meta `thread=6-32,face=case,fan=<k>`. These line up with a case's 120 mm fan holes.
- `A_PORT_RAD_0..1@A_RAD_0`: the tube ports on the -X tank, forward -X.
- `A_PLUG_RADFAN_0@A_RAD_0`: the one plug of the daisy-chained radiator fans (`kind=fan4,target=CPU_OPT,chain=<n>`).
- `A_HIT_1@A_RAD_0`: the radiator with its fans.

**Mounting in case_breeze:** case_breeze has fans at `A_FAN_1..3` on the front (centres y = 0.352, 0.230, 0.108,
x -0.1869, forward -x) and `A_FAN_0` at the rear; it has no top fan positions. A 360 radiator replaces the three
front fans: `A_RAD_FAN_0..2` go on `A_FAN_3, A_FAN_2, A_FAN_1` (or reversed to put the ports at the top), the
radiator's +Z (fan side) facing +x, into the case, so the fans pull air in through the radiator (the -Z face with
`A_HOLE_RAD_*` against the front panel). A 240 uses `A_FAN_1..2` (ports at the top, by the pump). The breeze fans
sit 0.122 m apart and a radiator's 0.120 m: snap fan 0 and let the others sit 2 mm off, or add radiator-specific
mount points to the case later. Cases with top fan positions take the radiator the same way with +Z facing down.

## New contracts: server heatsinks (`heatsink_spv`, `heatsink_l46`)

Shared frame: origin at the centre of the base contact face (on the CPU's IHS), +z away from the board, x = the
chassis airflow direction (front -> rear), y across. Passive: the server's fan wall cools them.
- `A_SCREW_<drive>_n`: captive spring screws (moving piece `screw@...`, the spring static), the anchor on the screw
  head, forward +z. Meta `spring=1,thread=M4,drive=T20|T30,torque=<N m>,order=<k>`: tighten in `order` 1, 2, 3...
  (cross pattern) and loosen in reverse.
- `A_FILM_0`: the clear cover over the pre-applied thermal compound (moving piece, peel from +x; meta
  `covers=preapplied_tim`).
- `A_AIRFLOW_0`: forward = the direction the air must flow, meta `passive=1,needs_cfm=..,height_class=1U|2U`.
- `A_HIT_0`: the body.

**SP-V (Arc Epoch), `cooler_srv_epoch_1u`:** 92.4 (x) x 118 (y) x 27 mm, copper base 6 mm and copper skived fins
along x, cut back round the screws. Six Torx T20 screws `A_SCREW_T20_0..5` at x = +-0.0385, y = +0.051, 0, -0.051
(heads at z 0.0129, sequence 1 (+x,+y), 2 (-x,+y), 3 (+x,0), 4 (-x,0), 5 (+x,-y), 6 (-x,-y)). The real SP5
reference coolers also use six T20 screws; this exact pitch is this task's own design. **What the socket needs:**
the SP-V socket (CPU task) and the Strata SP-V board (board task) put six M4 threaded studs/holes at these six
points relative to `A_SOCKET_COOLER_0`, with the package's long side (75 mm) along y.

**L46 (Tiron Platinum), `cooler_srv_platinum_2u`:** 78 (x) x 108 (y) x 67 mm: a copper base with four ears, five
6 mm heat pipes U-bent into 24 horizontal aluminium fins (air flows between them along x), four Torx T30 screws
`A_SCREW_T30_0..3` at (+-0.0345, +-0.047) in wells through the stack (heads at z 0.0129, sequence (+x,+y),
(-x,-y), (+x,-y), (-x,+y)). The 69 x 94 mm pattern is a narrow-ILM-style layout chosen here (real LGA4677 narrow
ILM is about 69 mm wide); the long axis (y) follows the 61 x 105 mm package. **What the socket needs:** the L46
socket's ILM carries four M4 studs at these points relative to `A_SOCKET_COOLER_0`.

## Deviations

- Server heatsinks: the screw heads are a six-sided captive head with a recess ring (the shared helpers have no
  hexalobe recess); the drive is in the meta. Their category is `Server` (they are not desktop coolers).

- AIOs: the real Corsair pump also has a USB and a SATA lead; here it has the pump 4-pin and one ARGB lead. The
  Arctic pump's small VRM fan and its fan cables run inside the tube sleeve on the real one; here the radiator fans
  have their own daisy-chained lead.

- `cooler_tiron_stock`: the real Laminar RM1 clips in with four push pins; here it keeps cooler_stock's four spring
  screws (same poses and meta) so the game installs it like the Spinner. Its paste is three stripes inside the same
  `A_PASTE_PRE_0` area. `game.socket` is L17 (it ships with the Tiron CPUs; the holes fit both boards).

- `cooler_noctis_l9` is a low-profile cooler on the tower contract: the X bracket is a flat plate under the fin stack
  and the four spring screws keep their exact poses in wells cut through the fins (as on the real NH-L9). Its fan
  lies on top, so `A_FAN_0` faces +z, and with no top cover `A_FILM_TOP_0` sits on the fan hub (meta `on=fan_hub`).

- Fans hang on steel wire clips on every tower (the Arctic original clips its fan with plastic brackets).
- Noctis browns and beiges have no plain tag; they are solid swatches of `tex_<id>_col` (one extra PNG per model).

## Rebuild

    blender -b --factory-startup -P Tools/Blender/build_cat_coolers.py -- [ids] [--nopreview]

(On Linux without Blender: `python3.11 -m venv ~/bpyenv && ~/bpyenv/bin/pip install bpy==5.0.1`, then run the
script through a runner that sets `bpy.app.binary_path`; see the task notes.)

## README line

- `build_cat_coolers.py` - the catalogue CPU coolers: Arctiq, Glacier, Noctis and Frostpeak air towers, the Tiron
  stock cooler, three AIO liquid coolers and two server heatsinks (`docs/reports/cat_coolers.md`).

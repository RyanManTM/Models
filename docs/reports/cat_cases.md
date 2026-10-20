# Catalogue 17: cases and fans

Script: `Tools/Blender/build_cat_cases.py` (new), plus optional style hooks in `Tools/Blender/build_case.py`.
Catalogue data: `docs/catalog/cases.json` (14 entries). Anchor report: `Logs/ModelPreviews/cat_cases_report.txt`.

## Status

| id | done | triangles | meshes | contract | vs sibling |
|---|---|---|---|---|---|
| case_lumin_216 | yes | 99,168 | 84 | case (case_breeze) | 63 SAME, front fans differ (below) |
| case_phanta_g360a | yes | 110,284 | 89 | case (case_breeze) | 67 SAME |
| case_nexa_h5 | yes | 93,334 | 83 | case (case_breeze) | 62 SAME, front fans differ |
| case_facet_fjord | not yet | | | case | |
| case_hush_500dx | not yet | | | case | |
| case_facet_fizzair | not yet | | | case | |
| case_brickhouse_beige98 | not yet | | | case | |
| fan_arctiq_p12 | not yet | | | case_fan (new) | |
| fan_noctis_a12x25 | not yet | | | case_fan (new) | |
| fan_noctis_a12x25_black | not yet | | | case_fan (new) | |
| fan_lumin_sl120_white | not yet | | | case_fan (new) | |
| fan_corvex_af120_rgb | not yet | | | case_fan (new) | |
| fan_arctiq_p14 | not yet | | | case_fan (new) | |
| fan_hush_wing4_140 | not yet | | | case_fan (new) | |

## Cases (contract: case, as case_breeze)

Every case is `build_case.build()` with a new style, so the frame (0.42 × 0.45 × 0.21, origin at the bottom centre,
−x front, window +z, feet 8 mm below the origin), the chassis, the board, PSU, slot, I/O-shield, SSD, grommet,
standoff, panel, front I/O, front-panel plug and hitbox anchors are case_breeze's exactly. Only the front fans move.

### Anchor comparison against case_breeze (`anchor_compare.py`)

| id | SAME | DIFF | only in the new case | only in case_breeze |
|---|---|---|---|---|
| case_lumin_216 | 63 | A_FAN_1, A_FAN_2 (160 mm at y 0.318 / 0.155; breeze 120 mm at 0.352 / 0.230) | – | A_FAN_3, A_PLUG_FAN_3 |
| case_phanta_g360a | 67 | – | – | – |
| case_nexa_h5 | 62 | A_FAN_1, A_FAN_2 (120 mm at y 0.300 / 0.170); A_FAN_0..2 meta without `rgb=1` (plain fans) | – | A_FAN_3, A_PLUG_FAN_3 |

Fan differences (allowed: front, top and bottom only; the rear A_FAN_0 / A_PLUG_FAN_0 are always SAME):

- **case_lumin_216**: two 160 mm ARGB front fans, A_FAN_1..2 (size 0.16), plugs A_PLUG_FAN_1..2 where breeze has them.
- **case_phanta_g360a**: as case_breeze (three 120 mm ARGB front fans, one rear).
- **case_nexa_h5**: two 120 mm front fans, A_FAN_1..2 at y 0.300 / 0.170; no RGB, so no `rgb=1` in the fan meta.

### Looks
- **case_lumin_216** (Lumin Airwave 216 RGB): black, a fine black hex-mesh front with two thin side grooves and the
  logo on the solid base band, two 160 mm ARGB fans behind it, rail feet, an ARGB line on the PSU shroud edge.
- **case_phanta_g360a** (Phanta Umbra G360A): black, a black round-hole mesh front, three ARGB fans, an ARGB strip
  in a black channel down the front's edge, an ARGB line on the shroud edge, the PHANTA logo on the base band.
- **case_nexa_h5** (Nexa H5 Draft): white, a white perforated (round-hole) steel front, white non-RGB fans, rail feet,
  a small NEXA logo.

### build_case.py hooks
Optional style keys, absent on case_brickhouse, case_breeze and case_aero:

- `front_fans = [(y, d), ...]` the front intake fans (heights and sizes) instead of the three 120 mm fans at
  `FRONT_FANS_Y`; their plugs rest where breeze's do.
- `front_wall(ns, holes) -> holes` the front wall's cut-outs; `face(ns)` the front face decoration (instead of the
  breeze mesh insert / brickhouse inlay); `feet(ns)` instead of the four feet; `extra(ns)` more looks before the
  hitboxes. `ns` is a namespace of `build()`'s locals.

Proof that the three existing cases are unchanged: the old and the new `build_case.py` both exported
case_brickhouse, case_breeze and case_aero on Linux into scratch folders, and `extras_compare.py` says
`SAME (138 objects)`, `SAME (157 objects)`, `SAME (157 objects)`. Those re-exports are not committed.

## New contract: case_fan

(Written in the style of `docs/MODEL_PIPELINE.md` §2.)

### Case fan: `fan_<brand>_<model>` (120 or 140 mm, 25 mm deep)
**Frame:**
- Origin at the frame centre. +Z is the airflow direction: the intake face (hub sticker side) is at z −0.0125, the
  exhaust face (motor, struts, label) at z +0.0125. +Y is up, the cable leaves at a lower corner.

**Anchors:**
- `A_FAN_0` the rotor (moving piece `fan_rotor@A_FAN_0`, plus its hub sticker), at the origin, local +Z = the intake
  side (model −Z), exactly like a case's or cooler's `A_FAN_<n>`: to install the fan into a case slot, put the fan's
  `A_FAN_0` pose on the case's `A_FAN_<n>` pose. Meta `axis=z,spin=-1,rpm=<max>` and `rgb=1` on ARGB fans.
- `A_HOLE_0..3` the four screw holes (frame corners: 0 top-left, 1 top-right, 2 bottom-left, 3 bottom-right, seen
  from +Z), on the intake face, local +Z = the intake side, size covers the frame depth. Spacing 105 mm (120 mm fans)
  and 124.5 mm (140 mm fans; the "125 mm" standard). Meta `d=0.0043,spacing=<m>,through=1,screw=fan`: the screw can
  come from either face.
- `A_PLUG_FAN_0` the loose 4-pin PWM plug where it rests below the fan (plug contact face at the anchor, local +Z back
  along the cable), meta `kind=fan4,pinout=GND|12V|TACH|PWM,fan=0`. It mates with a board's `A_PORT_FANSYS_<n>`.
- ARGB fans: `A_PLUG_ARGB_0`, a 3-pin 5 V ARGB plug (1×4 at 2.54 mm, position 3 the key), meta
  `kind=argb3,pinout=5V|D|KEY|GND,v=5,fan=0`. It mates with a board's `A_PORT_RGB_0` (`argb=5v`).
- Daisy-chain fans (`fan_lumin_sl120_white`): `A_PORT_LINK_0` (socket, −x side wall, local +Z = −x) and
  `A_PLUG_LINK_0` (tongue, +x side wall, local +Z = +x), meta `chain=link,mate=...,pitch=<m>,carries=pwm+argb`:
  slide the next fan's link socket onto this fan's tongue, the frames `pitch` apart. Only the first fan of a chain
  plugs in its A_PLUG_FAN_0 / A_PLUG_ARGB_0.
- `A_HIT_0` the frame box.

**Packs:** one fan model per product; `game.per_box` in the catalogue is the count in the box.

## Deviations
- New material colours that no plain tag has (walnut, Noctis brown, the teal accent, orange corners) come from an
  own palette texture `cat_cases_palette.png` (tag `tex_cat_cases_palette`, solid-swatch UVs) and, for the walnut
  slats, a grain texture `tex_case_facet_fjord_wood`.
- `build_cat_cases.py` lowers the Cycles samples of build_case's beauty previews to 40 (runtime only).

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_cases.py -- [ids...] [--nopreview]
```

## README line

| `build_cat_cases.py` | Catalogue 17: cases `case_lumin_216/phanta_g360a/nexa_h5/facet_fjord/hush_500dx/facet_fizzair/brickhouse_beige98` (`build_case.py` styles) and case fans `fan_arctiq_p12/p14`, `fan_noctis_a12x25(_black)`, `fan_lumin_sl120_white`, `fan_corvex_af120_rgb`, `fan_hush_wing4_140` (`parts_fan.py`) |

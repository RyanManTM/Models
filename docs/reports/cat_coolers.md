# Catalogue 16: CPU coolers

Branch `claude/cat-coolers`. Script `Tools/Blender/build_cat_coolers.py` (new; it imports `build_cooler.py`'s
`spring_screw` and `box` and wraps `parts_fan.make_fan`; no existing builder was edited). Catalogue data:
`docs/catalog/coolers.json`. Anchor report: `Logs/ModelPreviews/cat_coolers_report.txt`.

## Status

| # | id | contract | status |
|---|---|---|---|
| 1 | `cooler_arctiq_34_black` | cooler_tower | done |
| 2 | `cooler_arctiq_34_white` | cooler_tower | done |
| 3 | `cooler_glacier_ak400_white` | cooler_tower | not yet |
| 4 | `cooler_glacier_ak620_black` | cooler_tower | not yet |
| 5 | `cooler_noctis_d15` | cooler_tower | not yet |
| 6 | `cooler_noctis_d15_black` | cooler_tower | not yet |
| 7 | `cooler_noctis_l9` | cooler_tower | not yet |
| 8 | `cooler_frostpeak_120_rgb` | cooler_tower | not yet |
| 9 | `cooler_tiron_stock` | cooler_stock | not yet |
| 10 | `cooler_arctiq_lc240` | AIO (new) | not yet |
| 11 | `cooler_corvex_h150i_white` | AIO (new) | not yet |
| 12 | `cooler_glacier_ls720` | AIO (new) | not yet |
| 13 | `cooler_srv_epoch_1u` | server heatsink SP-V (new) | not yet |
| 14 | `cooler_srv_platinum_2u` | server heatsink L46 (new) | not yet |

## Models

| id | tris | height | contract | anchors vs sibling |
|---|---|---|---|---|
| `cooler_arctiq_34_black` | 36 672 | 157 mm | cooler_tower | vs `cooler_tower`: SAME 7, DIFF 4 (fan, hitboxes, top film: the free axes) |
| `cooler_arctiq_34_white` | 36 672 | 157 mm | cooler_tower | as the black one |

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
- `A_FILM_TOP_0`: the clear film on the label cover (anchor only).
- `A_HIT_n`: one per fin stack, one per fan, then the base.
- Total height <= 165 mm (the specs give each one's height).

## Deviations

- Fans hang on steel wire clips on every tower (the Arctic original clips its fan with plastic brackets).
- Noctis browns and beiges have no plain tag; they are solid swatches of `tex_<id>_col` (one extra PNG per model).

## Rebuild

    blender -b --factory-startup -P Tools/Blender/build_cat_coolers.py -- [ids] [--nopreview]

(On Linux without Blender: `python3.11 -m venv ~/bpyenv && ~/bpyenv/bin/pip install bpy==5.0.1`, then run the
script through a runner that sets `bpy.app.binary_path`; see the task notes.)

## README line

- `build_cat_coolers.py` - the catalogue CPU coolers: Arctiq, Glacier, Noctis and Frostpeak air towers, the Tiron
  stock cooler, three AIO liquid coolers and two server heatsinks (`docs/reports/cat_coolers.md`).

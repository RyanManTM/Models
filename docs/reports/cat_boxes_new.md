# Catalogue 19, helper group "new consumer box kinds" (`rig_new.py`)

Brief: `docs/tasks/catalog/19-boxes.md` (the new kinds: AIO, 3.5" HDD retail and bulk, fan packs, SFX PSU). Module
`Tools/Blender/rig_new.py` (plugged into `build_boxes.RIG_MODULES`), branch `claude/boxes-new`.

## Status

| kind | ids | state |
|---|---|---|
| `hdd` | hdd_seacrest_2tb, hdd_westline_4tb, hdd_seacrest_8tb | hdd_seacrest_2tb done; the others not built yet |
| `hdd_bulk` | hdd_seacrest_exos_20tb | done |
| `fan_pack` | fan_arctiq_p12_5pack, fan_noctis_a12x25, fan_noctis_a12x25_black, fan_lumin_sl120_white_3pack, fan_corvex_af120_rgb_3pack, fan_arctiq_p14, fan_hush_wing4_140 | not built yet |
| `aio` | cooler_arctiq_lc240, cooler_corvex_h150i_white, cooler_glacier_ls720 | not built yet |
| `psu_sfx` | psu_corvex_sf750 | not built yet |

## Boxes

Size is `A_HIT_0` (x × y × z, metres; the catalogue's `box_size`). The opening sequence gives each step's `order` in
brackets; every piece also carries `under=` (what covers it).

| box | size | tris | opening sequence (order) |
|---|---|---|---|
| `box_hdd_seacrest_2tb` | 0.215 × 0.05 × 0.13 | 5722 | two round seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> 2 papers lying on the tray (3..4) -> the drive A_ITEM_PART_0 in its silver anti-static bag and the screw bag A_ITEM_HW_0 (5) -> the moulded pulp tray A_INSERT_PULP_0 (6). |
| `box_hdd_seacrest_exos_20tb` | 0.215 × 0.06 × 0.135 | 668 | tape strip 0 (A_TAPE_0..2) (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile on the caps (3..4) -> the drive in its silver anti-static bag A_ITEM_PART_0, lifted out WITH its two black PE foam end caps (5) -> caps A_INSERT_FOAM_0/1 pulled off along -x/+x (6). |

## Rig designs

### `hdd`: 3.5" desktop drive, retail
- **Box:** a printed tuck-top box lying flat (the CPU box's construction: `tuck_walls`, `tuck_lid_top`, `dust_flaps`),
  a thumb notch in the front wall, two round clear seals over the lid's front edge. Size from the drive: x = length +
  68 mm (the screw pocket beside the drive), y = height + 22 mm, z = width + 26 mm.
- **Insert:** one moulded pulp tray (`A_INSERT_PULP_0`, real 1.5 mm wall, flange with a turned-down lip): a deep pocket
  for the drive with finger scoops on both long sides, a shallow pocket at +x for the screw bag.
- **Contents:** the drive label up, connectors to -x, in a silver anti-static bag (`bag=antistatic_silver`, parent the
  tray); the screw bag `A_ITEM_HW_0` ("4 x 6-32 SCREWS"); the papers (guide, warranty) lying on the tray's flange over
  both pockets (`floor_papers`: side by side when they fit, else a pile).
- **Words:** capacity, rpm and cache, read speed, interface, recording (CMR/SMR, helium), workload for the NAS line;
  badges capacity, rpm, NAS. Product shot: the drive label up from above.

### `hdd_bulk`: enterprise 3.5" drive, bulk pack
- **Box:** a brown single-wall carton (`rsc_box`, 3 mm board, brown packing tape strip), printed in the plain OEM
  style on kraft (`style=oem`, `oem_base=kraft`): the brand in one ink, the white product label (P/N, bar code, S/N,
  QTY, ESD mark) on the front and one end.
- **Inserts:** two black PE foam end caps (`A_INSERT_FOAM_0/1`, `with=A_ITEM_PART_0`), each a block with a pocket for
  the drive's end and a finger slot on top; the drive floats in the middle of the box between them.
- **Contents:** the drive in a silver anti-static bag; the papers in a pile on the caps.

## Deviations
- None yet.

## Requests for the shared code
- None yet.

## Rebuild
```
<python> run_bpy.py Tools/Blender/build_boxes.py -- kind:hdd kind:hdd_bulk kind:fan_pack kind:aio kind:psu_sfx
```
(`blender -b --factory-startup -P Tools/Blender/build_boxes.py -- ...` on Windows; `--noshots` reuses the cached
product shots, `--nopreview` skips the previews.)

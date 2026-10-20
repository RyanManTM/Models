# Catalogue 19, helper group "new consumer box kinds" (`rig_new.py`)

Brief: `docs/tasks/catalog/19-boxes.md` (the new kinds: AIO, 3.5" HDD retail and bulk, fan packs, SFX PSU). Module
`Tools/Blender/rig_new.py` (plugged into `build_boxes.RIG_MODULES`), branch `claude/boxes-new`.

## Status
**All 15 boxes of this group are built** (`rig.check()` prints no `RIG CHECK` line for any of them).

| kind | ids | state |
|---|---|---|
| `hdd` | hdd_seacrest_2tb, hdd_westline_4tb, hdd_seacrest_8tb | done |
| `hdd_bulk` | hdd_seacrest_exos_20tb | done |
| `fan_pack` | fan_arctiq_p12_5pack, fan_noctis_a12x25, fan_noctis_a12x25_black, fan_lumin_sl120_white_3pack, fan_corvex_af120_rgb_3pack, fan_arctiq_p14, fan_hush_wing4_140 | done |
| `aio` | cooler_arctiq_lc240, cooler_corvex_h150i_white, cooler_glacier_ls720 | done |
| `psu_sfx` | psu_corvex_sf750 | done |

## Boxes

Size is `A_HIT_0` (x × y × z, metres; the catalogue's `box_size`). The opening sequence gives each step's `order` in
brackets; every piece also carries `under=` (what covers it).

| box | size | tris | opening sequence (order) |
|---|---|---|---|
| `box_hdd_seacrest_2tb` | 0.215 × 0.05 × 0.13 | 5722 | two round seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> 2 papers lying on the tray (3..4) -> the drive A_ITEM_PART_0 in its silver anti-static bag and the screw bag A_ITEM_HW_0 (5) -> the moulded pulp tray A_INSERT_PULP_0 (6). |
| `box_hdd_westline_4tb` | 0.215 × 0.05 × 0.13 | 5722 | as hdd_seacrest_2tb. |
| `box_hdd_seacrest_8tb` | 0.215 × 0.05 × 0.13 | 5722 | as hdd_seacrest_2tb (NAS line words: workload, NAS badge). |
| `box_psu_corvex_sf750` | 0.2 × 0.1 × 0.17 | 732 | tape strip 0 (A_TAPE_0..2) (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile on the pouch, booklet at the bottom (3..5), and in the +x compartment the power cord A_ITEM_CORD_0 (c13, twist tie), the screw bag A_ITEM_HW_0 and the SFX-to-ATX bracket A_ITEM_ACC_0 (id=psu_bracket_sfx_atx, frame=model, clear bag) standing (3) -> cable pouch A_ITEM_POUCH_0 (6) -> the unit in its fabric bag A_ITEM_PART_0, lifted out WITH its two EPS saddle caps (7) -> caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| `box_hdd_seacrest_exos_20tb` | 0.215 × 0.06 × 0.135 | 668 | tape strip 0 (A_TAPE_0..2) (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile on the caps (3..4) -> the drive in its silver anti-static bag A_ITEM_PART_0, lifted out WITH its two black PE foam end caps (5) -> caps A_INSERT_FOAM_0/1 pulled off along -x/+x (6). |
| `box_fan_arctiq_p12_5pack` | 0.14 × 0.145 × 0.17 | 1152 | (5 fans, window box): round seal A_SEAL_0 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> from the back pocket: 2 papers standing at the back wall and 1 accessory (20 x FAN SCREWS) standing against the tray (3), and the die-cut card tray A_INSERT_CARD_0 lifted out (3) -> the fans A_ITEM_PART_0..4 out of the tray (4). |
| `box_fan_noctis_a12x25` | 0.14 × 0.145 × 0.055 | 1152 | (1 fan, window box): round seal A_SEAL_0 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> from the back pocket: 2 papers standing at the back wall and 3 accessories (4 x FAN SCREWS, LOW-NOISE ADAPTER, 4 x ANTI-VIBRATION MOUNTS) standing against the tray (3), and the die-cut card tray A_INSERT_CARD_0 lifted out (3) -> the fans A_ITEM_PART_0..0 out of the tray (4). |
| `box_fan_noctis_a12x25_black` | 0.14 × 0.145 × 0.055 | 1152 | (1 fan, window box): round seal A_SEAL_0 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> from the back pocket: 2 papers standing at the back wall and 3 accessories (4 x FAN SCREWS, LOW-NOISE ADAPTER, 4 x ANTI-VIBRATION MOUNTS) standing against the tray (3), and the die-cut card tray A_INSERT_CARD_0 lifted out (3) -> the fans A_ITEM_PART_0..0 out of the tray (4). |
| `box_fan_lumin_sl120_white_3pack` | 0.44 × 0.145 × 0.065 | 2584 | (3 fans, window box): round seal A_SEAL_0 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> from the back pocket: 2 papers standing at the back wall and 2 accessories (12 x FAN SCREWS, ARGB FAN CONTROLLER) standing against the tray (3), and the die-cut card tray A_INSERT_CARD_0 lifted out (3) -> the fans A_ITEM_PART_0..2 out of the tray (4). |
| `box_fan_corvex_af120_rgb_3pack` | 0.4 × 0.145 × 0.065 | 2596 | (3 fans, window box): round seal A_SEAL_0 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> from the back pocket: 2 papers standing at the back wall and 2 accessories (12 x FAN SCREWS, RGB FAN HUB) standing against the tray (3), and the die-cut card tray A_INSERT_CARD_0 lifted out (3) -> the fans A_ITEM_PART_0..2 out of the tray (4). |
| `box_fan_arctiq_p14` | 0.16 × 0.165 × 0.055 | 1144 | (1 fan, window box): round seal A_SEAL_0 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> from the back pocket: 2 papers standing at the back wall and 1 accessory (4 x FAN SCREWS) standing against the tray (3), and the die-cut card tray A_INSERT_CARD_0 lifted out (3) -> the fans A_ITEM_PART_0..0 out of the tray (4). |
| `box_fan_hush_wing4_140` | 0.16 × 0.165 × 0.055 | 1144 | (1 fan, window box): round seal A_SEAL_0 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> from the back pocket: 2 papers standing at the back wall and 2 accessories (4 x FAN SCREWS, 4 x ANTI-VIBRATION MOUNTS) standing against the tray (3), and the die-cut card tray A_INSERT_CARD_0 lifted out (3) -> the fans A_ITEM_PART_0..0 out of the tray (4). |
| `box_cooler_arctiq_lc240` | 0.385 × 0.105 × 0.43 | 6144 | tape strip 0 (A_TAPE_0..2) (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile on the card cover, booklet at the bottom (3..5) -> card cover A_INSERT_CARD_0 (6) -> the whole cooler A_ITEM_PART_0 (pump, tubes, radiator with its fans mounted, as one model) and the accessory box A_INSERT_ACCBOX_0 (7) -> the moulded pulp tray A_INSERT_PULP_0 and the accessory box's tuck flap A_FLAP_4 (8) -> mounting kit A_ITEM_HW_0 and the screw bag A_ITEM_HW_1 (9). |
| `box_cooler_corvex_h150i_white` | 0.5 × 0.09 × 0.43 | 6144 | tape strip 0 (A_TAPE_0..2) (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile on the card cover, booklet at the bottom (3..5) -> card cover A_INSERT_CARD_0 (6) -> the whole cooler A_ITEM_PART_0 (pump, tubes, radiator with its fans mounted, as one model) and the accessory box A_INSERT_ACCBOX_0 (7) -> the moulded pulp tray A_INSERT_PULP_0 and the accessory box's tuck flap A_FLAP_4 (8) -> mounting kit A_ITEM_HW_0 and the screw bag A_ITEM_HW_1 (9). |
| `box_cooler_glacier_ls720` | 0.5 × 0.09 × 0.43 | 6144 | tape strip 0 (A_TAPE_0..2) (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile on the card cover, booklet at the bottom (3..5) -> card cover A_INSERT_CARD_0 (6) -> the whole cooler A_ITEM_PART_0 (pump, tubes, radiator with its fans mounted, as one model) and the accessory box A_INSERT_ACCBOX_0 (7) -> the moulded pulp tray A_INSERT_PULP_0 and the accessory box's tuck flap A_FLAP_4 (8) -> mounting kit A_ITEM_HW_0 and the screw bag A_ITEM_HW_1 (9). |

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

### `psu_sfx`: SFX PSU
- **Box:** the ATX PSU rig (`rig_products.build_psu`, fully modular branch) at SFX size: a taped printed carton
  (`rsc_box`, clear tape), the unit fan up in a black fabric bag between two white EPS saddle caps (`eps_cap`, pockets
  of the unit's measured section; the +x cap stands 12 mm off the rear face so the switch sits in its pocket), the
  modular cable pouch on the unit and caps, the papers on the pouch.
- **The end compartment** (+x, between the rear cap and the end wall): the power cord coil and the screw bag standing
  against the cap, and the **SFX-to-ATX bracket** `A_ITEM_ACC_0` (`id=psu_bracket_sfx_atx`, `frame=model`: the
  anchor is the bracket model's own frame, so the game spawns `psu_bracket_sfx_atx.fbx` there) standing upright in a
  clear bag, its plate against the end wall.
- Size from the unit and the bracket: x = depth + 94 mm (caps and compartment), y = the bracket's height + 12 mm,
  z = the bracket's width + 16 mm.

### `fan_pack`: case fans, window box
- **Box:** a printed tuck-top box standing upright (lid hinged at the back top edge, a thumb notch in the front wall,
  one round clear seal over the lid's front edge, two dust flaps). The front wall has a **round window per fan**
  (radius 0.36 × the fan size, board and print cut alike) with a clear PET sheet glued behind it, so the fan's hub
  shows through (the closed previews place the fans for that reason: `rig_new.previews`).
- **Layout:** up to 3 fans stand side by side behind their windows (1-packs, 3-packs); the 5-pack stands its fans
  face to face, one behind the other, behind one window. Intake face (hub sticker) to the front.
- **Insert:** a die-cut card tray `A_INSERT_CARD_0` (floor, a front frame with round cut-outs, a back board with thumb
  slots, two sides, printed in the brand's field colour) that lifts out with the fans; one `A_ITEM_PART_n` per fan
  (`game.per_box`; the model is `it["model_id"]`, e.g. fan_arctiq_p12), `parent` the tray, `under` the tray.
- **The back pocket** (between the tray and the back wall): the papers standing at the back wall and the accessories
  standing in front of them, all reachable once the lid and dust flaps are open:
  - every pack: `A_ITEM_HW_0` "<4 × n> x FAN SCREWS";
  - Noctis: `A_ITEM_HW_1` "LOW-NOISE ADAPTER" (`kind=cable`) and `A_ITEM_HW_2` "4 x ANTI-VIBRATION MOUNTS";
  - Hush: `A_ITEM_HW_1` "4 x ANTI-VIBRATION MOUNTS";
  - Lumin SL120 3-pack: `A_ITEM_HW_1` "ARGB FAN CONTROLLER" (`kind=controller`, a white look mesh with its LED
    window and ports on the anchor);
  - Corvex AF120 RGB 3-pack: `A_ITEM_HW_1` "RGB FAN HUB" (`kind=hub`, a black look mesh).
- Size: x = cols × (fan + 6 mm) + 8 mm, y = fan height with its hanging plug + 12 mm, z = layers × 28 mm + the
  back pocket.

### `aio`: AIO liquid cooler
- **The model:** each AIO is **one model** (`docs/reports/cat_coolers.md`): the pump block is the root, the tubes are
  pieces on `A_TUBE_0/1`, and the radiator `A_RAD_0` carries its fans (`A_RAD_FAN_k@A_RAD_0`), in the shipped pose
  (radiator lying beside the pump at part y = -0.20, fans up). So the box spawns it once, `A_ITEM_PART_0` at that pose.
- **Box:** a taped printed carton (`rsc_box`, clear tape), the hero print on the top.
- **Insert:** a moulded pulp tray `A_INSERT_PULP_0` covering the floor, its flange 15 mm above the radiator's bottom,
  with three pockets: an L for the radiator, its fan plug and the tube loop past its end plus the tube channel up to
  the pump; a deeper pocket for the pump block and its leads; and the accessory compartment beside the pump.
- **The accessory box** `A_INSERT_ACCBOX_0` (`accessory_box`, tuck flap `A_FLAP_4`) stands in that compartment:
  `A_ITEM_HW_0` "MOUNTING KIT V5/L17" and `A_ITEM_HW_1` "<4 × fans> x FAN SCREWS, 8 x CASE SCREWS".
- **A card cover** `A_INSERT_CARD_0` (printed with the brand panel, a pull tab at the front) over the whole tray; the
  papers (manual, warranty, safety) in a pile on it.
- Size: the shipped pose's footprint plus margins; height = the cooler's height + 24 mm.

## Deviations
- **AIO fans:** the brief says "fans in a separate compartment". In the AIO models the fans are mounted on the
  radiator (one model, `A_RAD_FAN_k@A_RAD_0`), as the Arctiq unit really ships, so there are no separate fan items to
  box: the radiator lies with its fans in the pulp tray and the separate compartment holds the accessory box. If the
  cooler models ever split the fans off, add `A_ITEM_ACC_n` per fan in that compartment.
- **AIO bag:** none (`bag=none`): the code's bag is a box around the whole part's bounds, which would wrap pump, tubes
  and radiator together.
- **Fan box windows** hide part of the front print (the shared art does not know about the windows).

## Requests for the shared code
- `build_boxes.band_face`: with a wide logo (WESTLINE, ARCTIQ in their fonts) the logo runs into the product name on
  short faces (the HDD box front, the fan boxes' top): limit the logo to the space left of the name (or start the
  name after the logo's measured width).
- `build_boxes.compose`: an optional per-item list of window cut-outs (face, centre, radius) so the hero art can keep
  the logo and name clear of them (fan_pack).
- `rig_products.previews`: an option (e.g. `rig.contents_closed = True`) to place the contents before the closed
  shots; `rig_new.previews` copies the function to do this for the window boxes.

## Rebuild
```
<python> run_bpy.py Tools/Blender/build_boxes.py -- kind:hdd kind:hdd_bulk kind:fan_pack kind:aio kind:psu_sfx
```
(`blender -b --factory-startup -P Tools/Blender/build_boxes.py -- ...` on Windows; `--noshots` reuses the cached
product shots, `--nopreview` skips the previews.)

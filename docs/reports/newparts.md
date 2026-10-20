# Task 03 report: new parts to buy, with retail boxes

Four new catalog parts, each built by reusing an existing builder with a new spec or style, so they drop into the
game exactly like their siblings. Status: **done**.

| Part | Sibling(s) | Status |
|---|---|---|
| `cpu_arc9` | `cpu_arc5`, `cpu_arc7` | done |
| `gpu_rx77` | `gpu_rx66`, `gpu_rx88` | done |
| `case_aero` | `case_breeze` | done |
| `mb_ridge_x5` + `io_ridge_x5` | `mb_ridge_b5` + `io_ridge_b5` | done |
| `box_cpu_arc9`, `box_gpu_rx77`, `box_mb_ridge_x5`, `box_case_aero` | the sibling boxes | done |

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_parts_d.py -- [cpu_arc9 ...] [--nopreview]
```

With no ids, `build_parts_d.py` builds every part of this batch. It writes `Assets/Resources/Models/<id>.fbx`, the
textures, `Logs/ModelPreviews/<id>_<n>.png` and `Logs/ModelPreviews/<id>_report.txt` (every mesh with its
triangles, every anchor with position, axes, size and meta).

Anchor comparison against a sibling (used for the tables below):

```bash
blender -b --factory-startup -P Tools/Blender/anchor_compare.py -- Assets/Resources/Models/cpu_arc5.fbx Assets/Resources/Models/cpu_arc9.fbx
```

These models were built with Blender 5.0.1 as the `bpy` Python module (download.blender.org was blocked in the
cloud session); rebuilding a committed model this way gives an FBX that `extras_compare.py` reports SAME (for
example `plug_atx24`), so the module build matches the desktop Blender build.

---

## 1. `cpu_arc9`: ARC 9 9900X (Socket V5)

- **Script:** `build_parts_d.py` adds a spec to `build_cpu.SPECS` and calls `build_cpu.build`; `build_cpu.py` itself
  is unchanged.
- **Size:** 40 × 40 mm V5 LGA package, IHS top at z 0.006 (same package, outline and octopus IHS as arc5 and arc7).
- **Triangles:** 13,696 in 5 meshes (the same as arc5 and arc7).
- **Frame:** origin at the centre of the contact face, +z up, pin 1 at the (+x, −y) corner.
- **Textures:** `cpu_arc9_ihs.png` (new laser-etched markings: ARC logo, "ARC 9 9900X", "12-CORE",
  OPN 100-000001277, lot 9MK4813R50093, "DIFFUSED IN TAIWAN", "MADE IN MALAYSIA"); the substrate art is the shared
  `cpu_v5_pcb.png` (unchanged).

**Anchors**

| Anchor | Position | Size | Meta |
|---|---|---|---|
| `A_HIT_0` | (0, 0, 0.0030) | 0.040 × 0.040 × 0.0064 | |
| `A_MARK_PIN1_0` | (0.0193, −0.0193, 0.0012) | 0.006 × 0.006 × 0.002 | `corner=+x-y` |
| `A_PASTE_0` | (0, 0, 0.0060) | 0.030 × 0.030 × 0.002 | `ihs=0.0350x0.0380` |

**Anchor comparison** (`anchor_compare.py`): position, axes, size and meta of every anchor.

| Anchor | vs `cpu_arc5` | vs `cpu_arc7` |
|---|---|---|
| `A_HIT_0` | SAME | SAME |
| `A_MARK_PIN1_0` | SAME | SAME |
| `A_PASTE_0` | SAME | SAME |
| **Summary** | 3 / 3 SAME | 3 / 3 SAME |

**Suggested catalog data**

| Field | Value |
|---|---|
| Brand | ARC |
| Name | ARC 9 9900X |
| Socket | V5 (fits `mb_ridge_b5` and `mb_ridge_x5`) |
| Cores / threads | 12 / 24 |
| Clocks | 4.4 GHz base, 5.6 GHz boost |
| Cache | 64 MB L3 |
| Memory | DDR5 |
| TDP / power draw | 120 W TDP (about 160 W peak package power) |
| Price | $449 |
| Retail box | `box_cpu_arc9`, 0.11 × 0.07 × 0.11 (as the other CPUs) |

---

## 2. `gpu_rx77`: VOLTRA RX 7700 12GB (2.5-slot, triple fan)

- **Script:** `build_parts_d.py` adds a spec to `build_gpu.SPECS`; its look comes from style hooks in the spec
  (`backplate`, `overlay`, `skirts`, `logo`, `trim`). `build_gpu.py` was made configurable for this (see "Existing
  models unchanged" below): optional spec keys, absent on rx66/rx88, so those two cards build exactly as before.
- **Size:** 0.270 (x) × 0.0527 (y, fan face to backplate) × 0.118 (z) m; the PCB is 0.223 long (to x −0.128), the cooler
  runs past it to x −0.175 with a flow-through window in the backplate. 2.5 slots thick, on a 2-slot bracket.
- **Triangles:** 53,966 in 21 meshes (rx66 39,636; rx88 61,518).
- **Frame:** as rx66/rx88: origin at the PCIe contact edge, the bracket at x +0.095, the card runs towards −x, the cooler
  faces −y, the height runs along +z; gold fingers at y −0.001, z −0.002.
- **Look:** a gunmetal dark-grey shroud (`steel_dark`) with silver (`alu`) fan rings, silver edge rails, black wedges
  with silver chevrons between the fans and silver corner blades; three 78 mm 11-blade fans with VOLTRA hub stickers;
  five nickel heat pipes through an aluminium fin stack; a brushed silver backplate (`alu`) with a black VOLTRA print,
  four GPU-bracket screws and a hex-perforated flow-through window; a steel bracket with 3 × DP + HDMI and vent slots;
  the logo plate and RGB strip on the top edge; two PCIe 8-pin sockets on the top edge.
- **Texture:** `gpu_rx77.png` (logo plates, hub sticker, serial label, PCB back), from `build_gpu.make_texture`.

**Anchors** (Unity metres, card frame)

| Anchor | Position | Forward / up | Size | Meta |
|---|---|---|---|---|
| `A_PORT_PCIE8_0` | (−0.1005, −0.0066, 0.1120) | +z / +y | 0.0226 × 0.0126 × 0.012 | `pins=8,latch=+y` |
| `A_PORT_PCIE8_1` | (−0.0790, −0.0066, 0.1120) | +z / +y | 0.0226 × 0.0126 × 0.012 | `pins=8,latch=+y` |
| `A_PORT_DP_0..2` | (0.0965, −0.0046, 0.018 / 0.037 / 0.056) | +x / +y | 0.019 × 0.008 × 0.012 | `kind=displayport,chamfer=-y` |
| `A_PORT_HDMI_0` | (0.0965, −0.0046, 0.075) | +x / +y | 0.017 × 0.008 × 0.012 | `kind=hdmi,narrow=-y` |
| `A_SCREW_PH2_0` / `_1` | (0.1015, −0.0069 / −0.0272, 0.1065) | +z / +x | 0.008 cube | `slot=0` / `slot=1` |
| `A_FAN_0..2` | x −0.1248 / −0.0402 / 0.0443, y −0.0423, z 0.0600 | −y / +z | 0.078 × 0.078 × 0.013 | `axis=z,spin=-1,rpm=1900` |
| `A_FILM_BACKPLATE_0` | (−0.0408, 0.0029, 0.0605) | +y / +z | 0.2615 × 0.110 × 0.001 | `film=clear,peel_from=+x,chamfer=0.004@+x,screws=proud` |
| `A_FILM_SHROUD_0` | (−0.0070, −0.0426, 0.1184) | +z / +y | 0.0936 × 0.0121 × 0.001 | `film=clear,on=logo_plate,peel_from=-x` |
| `A_HIT_0` | (−0.0400, −0.0236, 0.0590) | | 0.270 × 0.0527 × 0.118 | (the card body) |
| `A_HIT_1` | (0.1010, −0.0166, 0.0465) | | 0.011 × 0.0392 × 0.120 | (the bracket) |
| `A_HIT_2` | (0, −0.0010, −0.0028) | | 0.090 × 0.003 × 0.006 | (the PCIe edge; `cap_pcie16` sits here) |

The fan rotors (`gpufan<n>_rotor@A_FAN_<n>#fan_black`) and hub stickers (`gpufan<n>_sticker@A_FAN_<n>#tex_gpu_rx77`)
are moving pieces of their fan anchors, as on the siblings.

**Anchor comparison** (`anchor_compare.py`; "same" = position, axes, size and meta identical)

| Anchor | vs `gpu_rx66` | vs `gpu_rx88` | Why it differs |
|---|---|---|---|
| `A_PORT_DP_0..2`, `A_PORT_HDMI_0` | SAME | SAME | |
| `A_SCREW_PH2_0..1` | SAME | SAME | |
| `A_HIT_1` (bracket), `A_HIT_2` (PCIe edge) | SAME | SAME | |
| `A_PORT_PCIE8_0` | position only (size and meta SAME) | rx88 has `A_PORT_12V2X6_0` instead | on this card's top edge, near the end of its PCB |
| `A_PORT_PCIE8_1` | new | new | the second 8-pin, 21.5 mm beside the first |
| `A_FAN_0..2` | position, size, rpm (rx66 has 2 fans) | position and size | three 78 mm fans on a 270 mm card |
| `A_FILM_BACKPLATE_0`, `A_FILM_SHROUD_0`, `A_HIT_0` | position and size | position and size | they follow the card's size |
| **Summary** | 8 SAME, 6 DIFF, 2 only in rx77 | 8 SAME, 6 DIFF, 1 only in rx88, 2 only in rx77 | |

**Suggested catalog data**

| Field | Value |
|---|---|
| Brand | VOLTRA |
| Name | VOLTRA RX 7700 12GB |
| Memory | 12 GB GDDR6, 192-bit |
| Clocks | 2.17 GHz game, 2.54 GHz boost |
| Outputs | 3 × DisplayPort 1.4, 1 × HDMI 2.1 |
| Power connectors | 2 × PCIe 8-pin |
| Board power / power draw | 245 W (recommended PSU 700 W) |
| Size | 270 mm, 2.5 slots |
| Price | $419 |
| Retail box | `box_gpu_rx77`, 0.36 × 0.09 × 0.17 (as the other GPUs) |

---

## 3. `case_aero`: AERO View 360 (panoramic ATX mid-tower)

- **Script:** `build_parts_d.py` adds a style to `build_case.STYLES` and calls `build_case.build`. `build_case.py` got
  optional style keys for it (absent on brickhouse and breeze, which rebuild identically, see below):
  `front="glass"`, `fans_bottom`, `bottom_fan_d`, `code`, `sn`, and the `BOTTOM_FANS` layout.
- **Size:** the case contract: 0.42 (x) × 0.45 (y) × 0.21 (z) body, bounds (−0.2193, −0.008, −0.1061) to
  (0.212, 0.4512, 0.1121), the same as `case_breeze`; origin at the bottom centre, −x front, window +z.
- **Triangles:** 110,668 in 89 meshes (`case_breeze` 111,788 in 89).
- **Look:** black painted steel (`paint_black`) and black plastic trim. The front is a panoramic glass pane between a
  black top strip (the front I/O, unchanged positions) and a black base strip (an `AERO` logo and an ARGB line), running
  to the window side where the side glass butts against it: no corner pillar. The side glass reaches forward to the
  front glass, its silkscreen bands line up with the front strips (none on the front edge). The front steel wall is a
  frame open behind the glass. Three 92 mm ARGB fans (black frames, `rgb` rings) lie on the PSU shroud blowing up,
  over round openings in the shroud top; a filtered hex intake in the bottom panel under the shroud's front half and a
  long magnetic filter under the whole floor feed them. A 120 mm ARGB rear fan, the slot covers, the PSU bay, the
  tray, grommets and 2.5" sleds are the breeze's.
- **Textures:** `case_aero_label.png` (rear label, model AR-V360), `case_aero_fanhub.png`, `case_aero_fanmotor.png`.

**Anchors:** all 67 of `case_breeze`'s anchors by name. 64 are identical (position, axes, size, meta), including
`A_SOCKET_MOBO_0`, `A_STANDOFF_0..9` (with the same `pre=` flags: A C F H K M pre-installed), `A_SOCKET_PSU_0`,
`A_SOCKET_IOSHIELD_0`, `A_SLOTCOVER_0..6` and `A_SCREW_PH2_0..6`, `A_PANEL_SIDE_0` with `A_SCREW_THUMB_0..1`,
`A_PANEL_BACK_0` with `A_SCREW_THUMB_2..3`, the front I/O (`A_BUTTON_POWER_0`, `A_BUTTON_RESET_0`, `A_LED_POWER_0`,
`A_LED_HDD_0`, `A_PORT_USBA_FRONT_0..1`), `A_FAN_0` (rear), `A_PLUG_FAN_0..3`, the six front-panel plugs,
`A_GROMMET_0..5`, `A_SOCKET_SSD25_0..1` and `A_HIT_0..5`. The full list with values is in
`Logs/ModelPreviews/case_aero_report.txt`.

**Anchor comparison** (`anchor_compare.py`, `case_breeze` → `case_aero`)

| Anchor | Result | case_breeze | case_aero |
|---|---|---|---|
| 64 anchors (everything else) | SAME | | |
| `A_FAN_1` | position, axes, size | (−0.1869, 0.352, 0), forward −x, 0.12 | (−0.042, 0.1168, 0.004), forward −y, up +x, 0.092 |
| `A_FAN_2` | position, axes, size | (−0.1869, 0.230, 0), forward −x, 0.12 | (0.052, 0.1168, 0.004), forward −y, up +x, 0.092 |
| `A_FAN_3` | position, axes, size | (−0.1869, 0.108, 0), forward −x, 0.12 | (0.146, 0.1168, 0.004), forward −y, up +x, 0.092 |
| **Summary** | 67 / 67 names; 64 SAME, 3 DIFF | | |

The fans' meta is unchanged (`axis=z,spin=-1,rpm=1200,rgb=1`) and their plugs `A_PLUG_FAN_1..3` rest exactly where the
breeze's front-fan plugs rest (`kind=fan4,fan=<n>`); the cables run along the shroud and up the tray's front edge.

**Suggested catalog data**

| Field | Value |
|---|---|
| Brand | AERO |
| Name | AERO View 360 |
| Form factor | ATX mid-tower (ATX / Micro-ATX / Mini-ITX) |
| Panels | Panoramic tempered glass front and side (no corner pillar), steel back panel |
| Fans included | 3 × 92 mm ARGB bottom intake, 1 × 120 mm ARGB rear exhaust |
| Front I/O | 2 × USB 3.0, USB-C, audio, power, reset |
| Clearances | GPU up to 360 mm, CPU cooler up to 160 mm |
| Power draw | about 6 W (four ARGB fans) |
| Price | $129 |
| Retail box | `box_case_aero`, 0.52 × 0.56 × 0.30 (as the other cases) |

---

## 4. `mb_ridge_x5` + `io_ridge_x5`: RIDGE X5 Elite (premium ATX, Socket V5, DDR5)

- **Script:** `build_parts_d.py` adds a config to `build_board.BOARDS` and builds it with `PremiumBoard`, a subclass of
  `build_board.Board` that only overrides look methods: `vrm`, `io_shroud`, `m2` (calls the B5's, then adds a second
  heatsink), `dimm_slot` and `pcie_slot` (call the B5's with other options). No method that creates an anchor is
  overridden, so the layout is the B5's by construction. `build_board.py` is unchanged.
- **Size:** ATX 0.244 × 0.305, PCB z 0..0.0016; bounds (−0.123, −0.1525, 0) to (0.1337, 0.1525, 0.0373).
- **Triangles:** 46,430 in 39 meshes (`mb_ridge_b5` 44,426 in 39; under the 50k board budget). `io_ridge_x5`: 1,244 in 1.
- **Frame:** as `mb_ridge_b5`: origin at the PCB centre, +z the component side, +x the rear I/O edge, +y the top edge.
- **Look:** a silver PCB (light grey solder mask, dark silkscreen "RIDGE X5 ELITE", DIMM/PCIe/SATA/F_PANEL labels as
  on the B5); white VRM heatsinks, taller and wider than the B5's (top: x −15..49, up to z 34 mm, B5 −12..46.5 and
  29 mm; rear: y 26..131, up to z 37 mm, B5 33..127 and 33 mm) with silver fin edges, a stepped cover and a silver
  inlay, the rear one level with the white I/O cover so the two read as one block; the white I/O cover with its RGB bar,
  logo plate and a silver strip; steel armour on both full-length PCIe slots; white DIMM slots and latches; the white
  M.2 heatsink plus a second one over the M2_2 slot (fixed, looks only); a white chipset heatsink. The cooler keep-out
  is respected: the heatsinks stay outside `A_SOCKET_COOLER_0`'s footprint as the B5's do (the rear one starts at the
  same x 0.0774), and the top one stays below the tower cooler's fin stack.
- **Textures:** `mb_ridge_x5_pcb.png` (PCB art), `mb_ridge_x5_marks.png` (chip marks, plates, pin field, PnP cap),
  `io_ridge_x5.png` (the shield's labels on bare brushed steel).
- **I/O shield `io_ridge_x5`:** `build_board.build_shield` on the X5's cut-outs (the B5's), unpainted steel with dark
  labels to go with the silver theme (the B5's is painted black). Frame as `io_ridge_b5`; `A_HIT_0` meta
  `board_pose=0.1279,0.07546,0.01999`.

**Anchor comparison** (`anchor_compare.py`)

| Model | vs | Result |
|---|---|---|
| `mb_ridge_x5` | `mb_ridge_b5` (committed FBX) | **80 / 80 SAME** (position, axes, size, meta), plus `A_FILM_IO_0` and `A_FILM_CHIPSET_0` |
| `mb_ridge_x5` | `mb_ridge_z4` | 60 SAME, 20 DIFF (the socket, DIMM notch and rear I/O differences between V5/DDR5 and L17/DDR4) |
| `io_ridge_x5` | `io_ridge_b5` | 1 / 1 SAME |

The 80 identical anchors include every ATX hole `A_HOLE_0..8` and screw `A_SCREW_PH2_0..8`, `A_SOCKET_CPU_0`,
`A_MARK_SOCKET_0`, `A_SOCKET_COOLER_0`, `A_LEVER_CPU_0`, `A_PLATE_CPU_0`, `A_COVER_CPU_0`, `A_SOCKET_RAM_0..3` with their
latches, `A_SOCKET_M2_0`, `A_STANDOFF_M2_0`, `A_COVER_M2_0` with its screws and film, `A_SOCKET_PCIE16_0`,
`A_LATCH_PCIE_0`, `A_SOCKET_PCIE1_0..1`, every internal port and header (ATX24, EPS8, CPU and SYS fans, F_PANEL,
USB3, HD audio, SATA 0..3, ARGB), every rear I/O anchor, the debug LEDs and `A_HIT_0..4`. The two film anchors are
the ones `build_board.Board.films()` defines for every board (PACKAGING.md §3: "the I/O cover and chipset films");
the committed `mb_ridge_b5.fbx`/`mb_ridge_z4.fbx` predate that method, so a re-export of those boards would gain the
same two anchors.

**Suggested catalog data**

| Field | Value |
|---|---|
| Brand | RIDGE |
| Name | RIDGE X5 Elite |
| Socket / chipset | V5 / RX670 |
| Memory | 4 × DDR5, up to 192 GB, 8000+ MT/s (OC) |
| Expansion | PCIe 5.0 x16 (armoured), PCIe 4.0 x16 (x4, armoured), 2 × PCIe x1 |
| Storage | 2 × M.2 NVMe with heatsinks, 4 × SATA 6 Gb/s |
| Networking | Wi-Fi 6E, 2.5G LAN |
| Rear I/O | as the B5 (BIOS flashback, 2 × USB 2.0, DP, HDMI, 4 × USB-A 5/10 Gb/s, 2 × USB-C, audio) |
| Power draw | about 15 W (board only) |
| Price | $289 |
| In the box | `io_ridge_x5`, 2 SATA cables, M.2 screws, papers; retail box `box_mb_ridge_x5`, 0.32 × 0.07 × 0.27 |

---

## 5. Retail box rigs

Built by `build_boxes.py` (new `ITEMS` entries) with the existing rig builders in `rig_products.py` (new
`PART_BOUNDS` entries; `ACC_SHELF` for the case). Each follows its sibling's kind, opening sequence and contents
(PACKAGING.md §3), keeps the sibling's `BoxSize`, and its printed art carries a product shot rendered from the new
part's own FBX (`shot from: <id>` in each box report). Rebuild:

```bash
blender -b --factory-startup -P Tools/Blender/build_boxes.py -- cpu_arc9 gpu_rx77 mb_ridge_x5 case_aero
```

Each box writes `box_<id>.fbx`, `tex_box_<id>` (the printed atlas), `tex_box_<id>_in` (inner prints), previews `_0.._1`
(closed), `_2` (opened, the part in place), `_3` (exploded) and `box_<id>_report.txt` (meshes, anchors with meta, the
opening sequence). They also rewrite the shared `box_seal.png` / `box_tape.png`, which are not committed (unchanged
art).

### `box_cpu_arc9` (as `box_cpu_arc5` / `box_cpu_arc7`)
- 0.11 × 0.07 × 0.11; 3,612 triangles in 13 meshes. Crimson and black print, the "9" numeral, "9900X", badges
  "12 CORES" / "SOCKET V5", the category stripe and an EAN barcode.
- Opening: seals `A_SEAL_0/1` (0) → tuck lid `A_FLAP_0` (1) → dust flaps `A_FLAP_1/2` (2) → tray `A_INSERT_CARD_0` and the
  papers `A_ITEM_DOC_0..2` (guide, warranty, sticker) (3) → clamshell lid `A_CLAMLID_0` (4) → the CPU `A_ITEM_PART_0`
  (5, `bag=none`) → clamshell base `A_INSERT_CLAM_0` (6).
- Anchors vs `box_cpu_arc7`: **13 / 13 SAME** (the same package bounds).

### `box_gpu_rx77` (as `box_gpu_rx66` / `box_gpu_rx88`)
- 0.36 × 0.09 × 0.17; 2,158 triangles in 5 meshes. Steel-blue sleeve with an ice-blue accent, badges "12 GB GDDR6" /
  "2 x 8-PIN".
- Opening: sleeve `A_SLEEVE_0` slides off +x (0) → lid `A_LID_0` (1) → the card in its silver bag `A_ITEM_PART_0`
  (2) → PE foam cradle `A_INSERT_FOAM_0` (3) → guide, driver note, sticker `A_ITEM_DOC_0..2` (4).
- Anchors vs `box_gpu_rx88`: 6 SAME; `A_ITEM_PART_0` (pose and size follow the shorter card: (0.0343, 0.0207,
  0.0525), 0.2895 × 0.0646 × 0.1399) and `A_INSERT_FOAM_0` (0.059 tall instead of 0.064, the card is thinner) differ.

### `box_mb_ridge_x5` (as `box_mb_ridge_b5`)
- 0.32 × 0.07 × 0.27; 502 triangles in 9 meshes. A dark steel-blue print (so the white board's product shot stands out)
  with an ice-blue accent, badges "SOCKET V5" / "DDR5" / "PCIe 5.0". The board ships in an anti-static silver bag, as
  the B5.
- Opening: side seals `A_SEAL_0/1` (0) → hinged lid `A_LID_0` (1) → the board in its bag `A_ITEM_PART_0` (2) → foam pad
  `A_INSERT_FOAM_0` (3) → tray `A_INSERT_CARD_0` (4) → the compartment: I/O shield `A_ITEM_ACC_0` (`id=io_ridge_x5`),
  SATA cables `A_ITEM_CORD_0` (`kind=sata`), M.2 screw bag `A_ITEM_HW_0`, poster, warranty card, sticker (5) → manual (6).
- Anchors vs `box_mb_ridge_b5`: 12 SAME; `A_ITEM_ACC_0` differs only in its meta (`id=io_ridge_x5`) and `A_ITEM_PART_0`
  only in its size (0.0448 instead of 0.0447 tall: the X5's rear heatsink is 0.1 mm taller than the B5's I/O cover).

### `box_case_aero` (as `box_case_breeze`)
- 0.52 × 0.56 × 0.30; 1,322 triangles in 17 meshes. The brown printed carton with a one-colour line-art print of the
  case (its three bottom fans visible), "AERO", "PANORAMIC ATX MID-TOWER", "VIEW 360" in the accent blue, the specs and
  handling marks on the sides, the shipping-label sticker.
- Opening (as the breeze): tape strip 0 (0) → long flaps (1) → short flaps (2) → the case in its clear bag
  `A_ITEM_PART_0`, lifted out by the foam (3) → EPS end caps `A_INSERT_FOAM_0/1` (`with=A_ITEM_PART_0`) (4) → the
  accessory box `A_INSERT_ACCBOX_0@A_ITEM_PART_0` inside the case, out through the side opening once the glass is off
  (`inside=A_PANEL_SIDE_0`) (5) → its flap (6) → standoff bag, screws, cable ties (7) → manual (8).
- Anchors vs `box_case_breeze`: 11 SAME; the accessory box and the five anchors inside it sit 26 mm higher, on top of the
  bottom fans instead of on the bare PSU shroud (`ACC_SHELF["case_aero"] = 0.1305` in `rig_products.py`). The box rides
  inside the case (the realistic option of PACKAGING.md §3), as on the other cases.

---

## Existing models unchanged

`build_gpu.py` (made configurable for `gpu_rx77`): `gpu_rx66` and `gpu_rx88` were re-exported into a scratch project
(`DCT_PROJECT`) with the unchanged script and with the edited script, and compared:

```
COMPARE gpu_rx66: SAME (37 objects)
COMPARE gpu_rx88: SAME (38 objects)
```

Their textures `gpu_rx66.png` and `gpu_rx88.png` are pixel-identical too (max difference 0).

`build_case.py` (made configurable for `case_aero`): `case_brickhouse` and `case_breeze`, re-exported the same way:

```
COMPARE case_brickhouse: SAME (138 objects)
COMPARE case_breeze: SAME (157 objects)
```

The comparisons are against a re-export from the unchanged script in the same environment because Linux re-exports
never match the committed Windows exports exactly: the unchanged scripts already differ in the text meshes
(Liberation fonts stand in for Agency FB, Eras, Segoe and Arial) and by float noise in a few swept meshes (heat pipes,
cables). None of the re-exports are committed.

`build_board.py`, `build_cpu.py` and `rig_common.py` are unchanged.

**The 20 existing box rigs** (`build_boxes.py` and `rig_products.py` gained the four new items, their part bounds and
`ACC_SHELF`; the new items are appended after the existing ones so those build in the same order). All 20 were
re-exported with the unchanged scripts and with the edited ones (`--noshots --nopreview`, the same placeholder product
shot for both, as the shot only feeds the textures), then compared with `extras_compare.py`:

```
COMPARE box_case_brickhouse: SAME (35 objects)
COMPARE box_case_breeze: SAME (35 objects)
COMPARE box_mb_ridge_b5: SAME (24 objects)
COMPARE box_mb_ridge_z4: SAME (24 objects)
COMPARE box_cooler_tower: SAME (36 objects)
COMPARE box_gpu_rx66: SAME (14 objects)
COMPARE box_gpu_rx88: SAME (14 objects)
COMPARE box_psu_750: SAME (32 objects)
COMPARE box_cable_dp: SAME (11 objects)
COMPARE box_fan_splitter: SAME (11 objects)
COMPARE box_cpu_arc5: CHANGED: changed=['clam_base@A_INSERT_CLAM_0#black_plastic.polys', '….uvs', 'clam_lid@A_CLAMLID_0#smoke_plastic.polys', '….uvs']
COMPARE box_cpu_arc7, box_cpu_tiron5: the same two meshes, .polys/.uvs only
COMPARE box_cooler_stock: clam_base / clam_lid .polys/.uvs only
COMPARE box_ram_ddr5_16, box_ram_ddr4_8, box_ssd_1tb: blister / blister_lid .polys/.uvs only
COMPARE box_psu_450: cap@A_INSERT_PULP_0/1 .polys/.uvs only
COMPARE box_ssd_sata_500: tray@A_INSERT_BLISTER_0 .polys/.uvs only
COMPARE box_usb_installer: blister@A_CLAMLID_0 .polys/.uvs only
```

The ten "CHANGED" rigs are not changed by the edits: the thermoformed shells (`rig_products.blister` / `formed` /
`R.shell`) come out with a different polygon order on every run. Two runs of the **unchanged** script give the same
`.polys/.uvs` differences on those meshes (checked on box_cpu_arc5, box_ram_ddr5_16, box_psu_450, box_ssd_sata_500), and
a shape comparison of the before/after exports (vertex positions, the set of polygons as vertex positions, surface
area, materials, per object) reports all ten IDENTICAL. Every anchor, every other mesh and every vertex is unchanged in
all 20 rigs.

## Deviations

1. **`case_aero` fans:** the brief asks for both "the same anchor names and positions as `case_breeze` (… fans …)" and
   "three bottom intake fans", which cannot both hold: the breeze's `A_FAN_1..3` are front fans, and a panoramic glass
   front has no front fans. The bottom fans keep the names `A_FAN_1..3` (and their plugs keep `A_PLUG_FAN_1..3`
   exactly), but sit on the PSU shroud facing down (forward −y). They are **92 mm**, not 120 mm: three 120 mm fans
   need 0.36 m of shroud, and the shroud's front 8 cm carries the 2.5" sled at `A_SOCKET_SSD25_0`, whose pose the
   contract fixes. Keeping every functional anchor (sockets, standoffs, screws, plugs, panels) identical won over the
   fan size. If 120 mm bottom fans matter more, the sled has to move (a change to `A_SOCKET_SSD25_0`).

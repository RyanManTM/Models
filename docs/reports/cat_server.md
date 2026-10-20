# Catalogue 18 report: server add-ins and gear

Script: `Tools/Blender/build_cat_server.py` with the helpers `cat_server_cards.py` (the PCIe cards and their brackets)
and `cat_server_rack.py` (the rack gear). The rack gear reuses `datacenter_common.py` (ports, ears, LEDs, buttons, fans,
atlases) and imports pieces of `datacenter_server.py` (PSU, drive tray, slide rails, lid, chassis, interior) and
`datacenter_net.py` (the RJ45 bank) unchanged. No hook was added to `build_datacenter.py` or any other builder, so no
existing model is touched or re-exported. Fit check: `Tools/Blender/cat_server_fit.py`. Catalogue data:
`docs/catalog/server.json` (15 parts). Combined anchor report: `Logs/ModelPreviews/cat_server_report.txt`.

## Status

All 14 catalogue items are built (15 ids: the blanking panel is two), plus the six loose low-profile brackets.

| Model | Size (x × y × z, m) | Triangles | Meshes | Anchors | Status |
|---|---|---|---|---|---|
| `nic_linkwave_350t2` | 0.139 × 0.018 × 0.120 | 4,446 | 19 | 13 | done |
| `nic_linkwave_710da2` | 0.179 × 0.018 × 0.120 | 4,710 | 20 | 13 | done |
| `nic_melnet_strand6_25g` | 0.179 × 0.018 × 0.120 | 4,726 | 20 | 13 | done |
| `nic_melnet_strand6_100g` | 0.179 × 0.019 × 0.120 | 5,446 | 20 | 13 | done |
| `hba_broadline_9500_16i` | 0.167 × 0.021 × 0.120 | 5,710 | 15 | 11 | done |
| `hba_broadline_9560_16i` | 0.240 × 0.021 × 0.120 | 6,420 | 18 | 13 | done |
| `nic_linkwave_350t2_lpbracket` | 0.012 × 0.018 × 0.079 | 564 | 4 | 4 | done |
| `nic_linkwave_710da2_lpbracket` | 0.012 × 0.018 × 0.079 | 900 | 4 | 4 | done |
| `nic_melnet_strand6_25g_lpbracket` | 0.012 × 0.018 × 0.079 | 900 | 4 | 4 | done |
| `nic_melnet_strand6_100g_lpbracket` | 0.012 × 0.018 × 0.079 | 900 | 4 | 4 | done |
| `hba_broadline_9500_16i_lpbracket` | 0.012 × 0.018 × 0.079 | 1,112 | 3 | 4 | done |
| `hba_broadline_9560_16i_lpbracket` | 0.012 × 0.018 × 0.079 | 1,112 | 3 | 4 | done |
| `srv_strata_sg840_4u` | 0.483 × 0.177 × 0.787 | 32,460 | 205 | 86 | done |
| `srv_strata_sr224_2u` | 0.483 × 0.087 × 0.779 | 24,602 | 244 | 118 | done |
| `srv_linkwave_ls4804x` | 0.483 × 0.044 × 0.284 | 18,958 | 113 | 168 | done |
| `srv_linkwave_ls1600x` | 0.483 × 0.044 × 0.304 | 14,024 | 49 | 68 | done |
| `srv_strata_shelf_1u` | 0.483 × 0.044 × 0.402 | 2,724 | 3 | 7 | done |
| `srv_strata_blank_1u` | 0.483 × 0.044 × 0.018 | 1,502 | 14 | 5 | done |
| `srv_strata_blank_2u` | 0.483 × 0.089 × 0.018 | 1,590 | 14 | 5 | done |
| `srv_strata_cma` | 0.447 × 0.038 × 0.146 | 2,750 | 13 | 6 | done |
| `srv_strata_kvm_1u` | 0.488 × 0.043 × 0.785 | 6,662 | 22 | 18 | done |


Sizes are the full bounds of each model, moving pieces included (rails, handles, the supercap pack).

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_server.py -- [ids...] [--nopreview]
blender -b --factory-startup -P Tools/Blender/cat_server_fit.py -- [--nopreview]
```

With no ids it builds all 21 models. Each writes `Assets/Resources/Models/<id>.fbx`, previews
`Logs/ModelPreviews/<id>_<n>.png` (0–1 Workbench, the rest Cycles) and `Logs/ModelPreviews/<id>_report.txt` (every mesh
and anchor, the bounds and the frame). Textures: `cat_server_cards.png` (card labels, logos, silkscreen, bracket legends,
the supercap label), `cat_server_rack.png` (logos, rating labels, port numbers, keyboard legends, the KVM screen, drive
and GPU labels) and `cat_server_sled_mesh.png` (the GPU sleds' perforation, alpha-cut). The servers also use the
existing `server_print.png` (DIMM faces, the lid's service label, the PSU label) and `parts_c_palette.png` (green touch
points); the build does not rewrite either.

Built in the cloud with the `bpy` 5.0.1 module under Python 3.11 (download.blender.org was blocked).

**README line** (for the scripts table):

```text
| `build_cat_server.py` | Catalogue 18, server add-ins and gear: NICs `nic_linkwave_350t2/710da2`, `nic_melnet_strand6_25g/100g`, the HBA and RAID cards `hba_broadline_9500_16i/9560_16i` (each with its loose `<id>_lpbracket`), servers `srv_strata_sg840_4u` (8 GPU sleds) and `srv_strata_sr224_2u`, switches `srv_linkwave_ls4804x/ls1600x`, the shelf, blanking panels, cable arm and KVM drawer `srv_strata_*` (`cat_server_cards.py`, `cat_server_rack.py`; `cat_server_fit.py` installs the rack gear in `rack_42u` as a fit check) |
```

## Fit check (`cat_server_fit.py`)

The script uses `datacenter_fit.py`'s functions (import, placement, hole check, render) with this family's layout. It
installs everything in `rack_42u` at `A_RACKU_n`, exactly as the game would:

| U | Device |
|---|---|
| 1–2 | `srv_strata_sr224_2u` |
| 3 | `srv_strata_blank_1u` |
| 4–7 | `srv_strata_sg840_4u` |
| 8–9 | `srv_strata_blank_2u` |
| 10 | `server_1u` (existing) with `srv_strata_cma` on its rails |
| 11 | `srv_strata_kvm_1u` |
| 12 | `srv_strata_shelf_1u` |
| 14 | `srv_linkwave_ls4804x` |
| 15 | `srv_linkwave_ls1600x` |
| 16 | `patch_panel_24` (existing) |
| 17 | `srv_strata_blank_1u` |

Checks: every `A_SCREW_RACK_n` / `A_SCREW_THUMB_n` (42 of them, the KVM's four rear-rail screws included) lands on a
rack hole within 1 mm; no two devices overlap in height; no vertex of the cable arm is inside the 1U server's chassis
(its `A_HIT_0` plus the 16 mm of the PSU handles); the arm's outer connector sits in the server's outer slide channel
(x 0.2215, at the rail's centre height, z −0.720 in the device frame).

Result: **FIT TOTAL: OK** (12 devices). Renders: `Logs/ModelPreviews/cat_server_fit_0/1.png` (front, the door and
the +x panel hidden) and `cat_server_fit_rear_0/1.png` (rear, the arm behind the 1U server).

## New contract: PCIe add-in card (`contract: pcie_card`)

The cards are a new part kind (the game can't install NICs or storage controllers yet), designed on the GPU contract
so the same slot logic will work.

- **Frame:** the GPU frame (`docs/MODEL_PIPELINE.md` §2, `build_gpu.py`). Origin at the PCIe contact edge, where the
  centre of an x16 edge would be, at the top of the slot. The card runs from the bracket at x +0.095 towards −x; its
  components face −y (the cooler side of a GPU); its height runs along +z away from the slot. PCB y −0.0018..−0.0002;
  the fingers z −0.0052..−0.0012. The fingers always start 0.0445 from the origin on the bracket side (the 11-pin
  segment, the key at x 0.0310..0.0328, then the long segment), so the key and the bracket are where a GPU's are, and
  a narrow card installs in any slot at least as wide at the same pose as a graphics card. The edge length per card:

  | Card | Lanes | Edge | Edge x range | Board (L × H) |
  |---|---|---|---|---|
  | `nic_linkwave_350t2` | x4 | 39 mm | 0.0055..0.0445 | 127.5 × 68.9 mm |
  | `nic_linkwave_710da2` | x8 | 56 mm | −0.0115..0.0445 | 167.6 × 68.9 mm |
  | `nic_melnet_strand6_25g` | x8 | 56 mm | −0.0115..0.0445 | 167.6 × 68.9 mm |
  | `nic_melnet_strand6_100g` | x16 | 89 mm | −0.0445..0.0445 | 167.6 × 68.9 mm |
  | `hba_broadline_9500_16i` | x8 | 56 mm | −0.0115..0.0445 | 155.6 × 68.9 mm |
  | `hba_broadline_9560_16i` | x8 | 56 mm | −0.0115..0.0445 | 155.6 × 68.9 mm |

  All six are single-slot low-profile boards (68.9 mm from the bottom of the fingers, z up to 0.0634).
- **Bracket:** every card ships with a full-height single-slot bracket fitted. It is the moving piece
  `bracket@A_BRACKET_0#…` of `A_BRACKET_0`: at the bracket's outer face (x 0.0965), on the slot-0 centre line
  (y −0.0069), at the full-height bracket's mid height (z 0.0465), model axes, size = the bracket; meta
  `remove=-z,swap=<id>_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full`. The plate is one slot wide
  (y +0.0030..−0.0154), with the GPU's bottom tongue and the GPU's folded tab (top at z 0.1065, the U slot open
  towards +x).
- **`<id>_lpbracket`:** the separate low-profile bracket (79.2 mm: the tongue 13.5 mm below the slot, the tab top at
  z 0.0657). Its frame **is** the card's `A_BRACKET_0` pose, so the swap is: remove the bracket piece, place
  `<id>_lpbracket` at `A_BRACKET_0`. It has the same port openings, screws and vents as the full-height one, its own
  `A_SCREW_PH2_0` (tab), `A_SCREW_PH1_0..1` and `A_HIT_0`.
- **Anchors:**
  - `A_SCREW_PH2_0`: the case-slot screw in the tab, exactly the GPU's slot-0 screw (x 0.1015, y −0.0069, z 0.1065,
    +z, up +x, `slot=0`). Proven SAME by `anchor_compare.py` (below).
  - `A_SCREW_PH1_0..1`: the two small screws on the bracket's outer face that hold the bracket to the cages (+x,
    `thread=4-40,holds=bracket`).
  - Ports at the bracket's outer face (x 0.0965), +Z out of the bracket (+x), **+Y away from the board (−y)**: the
    cage top, the RJ45 latch side (`latch=+up`). `A_PORT_ETH_n` (RJ45, `depth=0.012`), `A_PORT_SFP_n` (`depth=0.042`,
    `sfp=sfp+|sfp28`), `A_PORT_QSFP_n` (`depth=0.048`, `qsfp=qsfp28`); meta `speed=` and `port=` (1-based).
  - Each network port has `A_LED_LINK_n` (green) and `A_LED_ACT_n` (amber) with their lenses: in the RJ45 jack's
    face corners on the board side, or as light pipes in the bracket on the cage's outer side.
  - `A_PORT_SAS_n`: the internal SFF-8654 x8 receptacles standing on the top edge, mouth up (+z), +Y away from the
    board, meta `conn=sff8654,lanes=8,phys=0-7|8-15,latch=+up`; each with `A_LED_SAS_n` (green) below it.
  - RAID card only: `A_PORT_SUPERCAP_0` (the 6-pin header on the top edge, +z) and `A_SUPERCAP_0`, the supercap pack
    with its cable as a moving piece (meta `kind=supercap,cable=A_PORT_SUPERCAP_0,len=0.45,mount=chassis_clip,free=1`).
    In the model the pack lies beside the card's far end on its cable; the game moves it to a clip in the chassis and
    redraws the cable from `A_PORT_SUPERCAP_0`.
  - `A_HIT_0` (the board and its parts), `A_HIT_1` (the bracket, the GPU's box for one slot), `A_HIT_2` (the edge).
- **Looks:** a green board with the edge fingers on both faces (presence pins short), the controller under a finned
  heatsink with push pins and the brand printed on it, flash, regulators, inductors, MLCC rows, a crystal; magnetics
  behind the RJ45 jacks; PHYs behind the cages; SFP / SFP28 / QSFP28 cages with EMI gaskets (QSFP with riding fins);
  silkscreen and a serial / MAC label on the back; the 9560's cache daughter board with four DRAM chips.

### Anchor comparison with `gpu_rx66` (`anchor_compare.py`)

`nic_linkwave_710da2` against the sibling graphics card: the slot screw is SAME; the hit boxes differ in size (a
one-slot low-profile card); the rest are the card's own anchors.

| anchor | result | A pos | B pos |
|---|---|---|---|
| `A_BRACKET_0` | ONLY_B |  | (0.0965, -0.0069, 0.0465) |
| `A_FAN_0` | ONLY_A | (-0.0511, -0.0373, 0.0560) |  |
| `A_FAN_1` | ONLY_A | (0.0406, -0.0373, 0.0560) |  |
| `A_FILM_BACKPLATE_0` | ONLY_A | (-0.0058, 0.0029, 0.0565) |  |
| `A_FILM_SHROUD_0` | ONLY_A | (0.0055, -0.0390, 0.1104) |  |
| `A_HIT_0` | DIFF pos d=0.0302; size 0.20000,0.04770,0.11000 -> 0.16730,0.02240,0.06340 | (-0.0050, -0.0211, 0.0550) | (0.0110, -0.0106, 0.0317) |
| `A_HIT_1` | DIFF pos d=0.0104; size 0.01100,0.03920,0.12000 -> 0.01100,0.01840,0.12000 | (0.1010, -0.0166, 0.0465) | (0.1010, -0.0062, 0.0465) |
| `A_HIT_2` | DIFF pos d=0.0165; size 0.09000,0.00300,0.00600 -> 0.05600,0.00300,0.00600 | (0.0000, -0.0010, -0.0028) | (0.0165, -0.0010, -0.0028) |
| `A_LED_ACT_0` | ONLY_B |  | (0.0968, -0.0054, 0.0111) |
| `A_LED_ACT_1` | ONLY_B |  | (0.0968, -0.0054, 0.0509) |
| `A_LED_LINK_0` | ONLY_B |  | (0.0968, -0.0104, 0.0111) |
| `A_LED_LINK_1` | ONLY_B |  | (0.0968, -0.0104, 0.0509) |
| `A_PORT_DP_0` | ONLY_A | (0.0965, -0.0046, 0.0180) |  |
| `A_PORT_DP_1` | ONLY_A | (0.0965, -0.0046, 0.0370) |  |
| `A_PORT_DP_2` | ONLY_A | (0.0965, -0.0046, 0.0560) |  |
| `A_PORT_HDMI_0` | ONLY_A | (0.0965, -0.0046, 0.0750) |  |
| `A_PORT_PCIE8_0` | ONLY_A | (-0.0580, -0.0066, 0.1075) |  |
| `A_PORT_SFP_0` | ONLY_B |  | (0.0965, -0.0079, 0.0215) |
| `A_PORT_SFP_1` | ONLY_B |  | (0.0965, -0.0079, 0.0405) |
| `A_SCREW_PH1_0` | ONLY_B |  | (0.0976, -0.0079, 0.0071) |
| `A_SCREW_PH1_1` | ONLY_B |  | (0.0976, -0.0079, 0.0549) |
| `A_SCREW_PH2_0` | SAME | (0.1015, -0.0069, 0.1065) | (0.1015, -0.0069, 0.1065) |
| `A_SCREW_PH2_1` | ONLY_A | (0.1015, -0.0272, 0.1065) |  |

SUMMARY gpu_rx66.fbx vs nic_linkwave_710da2.fbx: 14 anchors in A, 13 in B; SAME 1, DIFF 3, ONLY_A 10, ONLY_B 9


The other cards give the same result for `A_SCREW_PH2_0` (SAME), e.g. `hba_broadline_9560_16i`:

| anchor | result | A pos | B pos |
|---|---|---|---|
| `A_BRACKET_0` | ONLY_B |  | (0.0965, -0.0069, 0.0465) |
| `A_FAN_0` | ONLY_A | (-0.0511, -0.0373, 0.0560) |  |
| `A_FAN_1` | ONLY_A | (0.0406, -0.0373, 0.0560) |  |
| `A_FILM_BACKPLATE_0` | ONLY_A | (-0.0058, 0.0029, 0.0565) |  |
| `A_FILM_SHROUD_0` | ONLY_A | (0.0055, -0.0390, 0.1104) |  |
| `A_HIT_0` | DIFF pos d=0.0338; size 0.20000,0.04770,0.11000 -> 0.15530,0.02240,0.06340 | (-0.0050, -0.0211, 0.0550) | (0.0170, -0.0106, 0.0317) |
| `A_HIT_1` | DIFF pos d=0.0104; size 0.01100,0.03920,0.12000 -> 0.01100,0.01840,0.12000 | (0.1010, -0.0166, 0.0465) | (0.1010, -0.0062, 0.0465) |
| `A_HIT_2` | DIFF pos d=0.0165; size 0.09000,0.00300,0.00600 -> 0.05600,0.00300,0.00600 | (0.0000, -0.0010, -0.0028) | (0.0165, -0.0010, -0.0028) |
| `A_LED_SAS_0` | ONLY_B |  | (-0.0270, -0.0022, 0.0484) |
| `A_LED_SAS_1` | ONLY_B |  | (0.0040, -0.0022, 0.0484) |
| `A_PORT_DP_0` | ONLY_A | (0.0965, -0.0046, 0.0180) |  |
| `A_PORT_DP_1` | ONLY_A | (0.0965, -0.0046, 0.0370) |  |
| `A_PORT_DP_2` | ONLY_A | (0.0965, -0.0046, 0.0560) |  |
| `A_PORT_HDMI_0` | ONLY_A | (0.0965, -0.0046, 0.0750) |  |
| `A_PORT_PCIE8_0` | ONLY_A | (-0.0580, -0.0066, 0.1075) |  |
| `A_PORT_SAS_0` | ONLY_B |  | (-0.0350, -0.0068, 0.0644) |
| `A_PORT_SAS_1` | ONLY_B |  | (-0.0040, -0.0068, 0.0644) |
| `A_PORT_SUPERCAP_0` | ONLY_B |  | (-0.0486, -0.0046, 0.0614) |
| `A_SCREW_PH1_0` | ONLY_B |  | (0.0976, -0.0057, 0.0100) |
| `A_SCREW_PH1_1` | ONLY_B |  | (0.0976, -0.0057, 0.0480) |
| `A_SCREW_PH2_0` | SAME | (0.1015, -0.0069, 0.1065) | (0.1015, -0.0069, 0.1065) |
| `A_SCREW_PH2_1` | ONLY_A | (0.1015, -0.0272, 0.1065) |  |
| `A_SUPERCAP_0` | ONLY_B |  | (-0.1106, -0.0060, 0.0260) |

SUMMARY gpu_rx66.fbx vs hba_broadline_9560_16i.fbx: 14 anchors in A, 13 in B; SAME 1, DIFF 3, ONLY_A 10, ONLY_B 9


## Rack gear: the rack device contract, and what is new

All rack gear uses the existing rack device frame (`docs/reports/datacentre.md`): origin at the centre of the front
mounting plane, at the bottom of the device's U space, +Z out of the front, +Y up, the body towards −Z; installs at a
rack's `A_RACKU_n`. Ears carry `A_SCREW_RACK_n` (fixed) or `A_SCREW_THUMB_n` (servers). Ports, LEDs, buttons, PSUs,
drive trays, lids and slide rails follow the data-centre conventions exactly; the PSU, drive tray, slide rail and lid
code is `datacenter_server.py`'s own. New anchor kinds:

- **`A_SLED_n`** (GPU server): a front-loading GPU sled, `pull=+z,dist=0.31,slot=n,gpu=double_width,blind_mate=1`.
  The whole sled (face, handle, release, carrier, the GPU and its blind-mate connector) is the moving piece; it carries
  `A_LED_SLED_n` (green) and `A_LED_SLEDFAULT_n` (amber).
- **`A_SHELF_0`** (shelf): the load surface, +Z up (+y), up = −z (into the rack), size = the usable area; meta
  `surface=1,w,d,load_kg=25,front_mount=1`. Items stand on it at the anchor's height.
- **`A_DRAWER_0`** (KVM): the slide-out drawer, `pull=+z,dist=0.450`. Nested: `A_LID_0@A_DRAWER_0` (the LCD lid,
  `hinge=x,open=-105`: a negative angle lifts the front edge), `A_SCREEN_0@A_LID_0@A_DRAWER_0` (screen down when
  closed, +Y towards the lid's free edge, so it is upright when open), `A_BUTTON_LCD_0@A_DRAWER_0`,
  `A_LED_POWER_0@A_DRAWER_0`.
- **The cable management arm** (`contract: rack_device`, `new_contract: true`): installed at the **same `A_RACKU_n`** as
  the 1U server whose rails it clips on. `A_MOUNT_OUTER_0` / `A_MOUNT_SUPPORT_0` (fixed, in the +x / −x outer slide
  channels behind the intermediate member, `insert=+z`), `A_ARM_0` (the outer arm, `hinge=y` at the +x connector),
  `A_ARM_1@A_ARM_0` (the inner arm, `hinge=y` at the elbow) and `A_MOUNT_INNER_0@A_ARM_1@A_ARM_0` (the plate that clips on the inner rail member's
  rear end at z −0.660, beside the chassis). Closed (server in), the arms lie folded behind the server between
  z −0.694 and −0.766.

## The cards

### nic_linkwave_350t2: Linkwave LW350-T2, dual-port 1GbE (analog: Intel I350-T2), x4

Two RJ45 jacks with their LEDs and magnetics, a small bare-aluminium heatsink, the blue Linkwave label on the back.

- **Triangles:** 4,446 in 19 meshes
- **Bounds:** min=(-0.0325, -0.0154, -0.0135) max=(0.1065, 0.0030, 0.1065) size=(0.1390, 0.0184, 0.1200)
- Frame: card (GPU frame), PCIe x4 edge 0.0390 m (x 0.0055..0.0445), board 0.1275 x 0.0689, low-profile board with a full-height bracket

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BRACKET_0` | (0.0965, -0.0069, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 | remove=-z,swap=nic_linkwave_350t2_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full |
| `A_HIT_0` | (0.0311, -0.0106, 0.0317) | +z / +y | 0.12720,0.02240,0.06340 |  |
| `A_HIT_1` | (0.101, -0.0062, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 |  |
| `A_HIT_2` | (0.025, -0.001, -0.0028) | +z / +y | 0.03900,0.00300,0.00600 |  |
| `A_LED_ACT_0` | (0.0968, -0.0037, 0.0171) | +x / -y | 0.00240,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_1` | (0.0968, -0.0037, 0.0356) | +x / -y | 0.00240,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_LINK_0` | (0.0968, -0.0037, 0.0259) | +x / -y | 0.00240,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_1` | (0.0968, -0.0037, 0.0444) | +x / -y | 0.00240,0.00200,0.00300 | colour=green,fn=link |
| `A_PORT_ETH_0` | (0.0965, -0.0084, 0.0215) | +x / -y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=1g,port=1 |
| `A_PORT_ETH_1` | (0.0965, -0.0084, 0.04) | +x / -y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=1g,port=2 |
| `A_SCREW_PH1_0` | (0.0976, -0.0084, 0.0102) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH1_1` | (0.0976, -0.0084, 0.0513) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH2_0` | (0.1015, -0.0069, 0.1065) | +z / +x | 0.00800,0.00800,0.00800 | slot=0 |

Moving pieces: `bracket_n@A_BRACKET_n#dark_plastic`, `bracket_n@A_BRACKET_n#nickel`, `bracket_n@A_BRACKET_n#steel`, `bracket_n@A_BRACKET_n#tex_cat_server_cards`, `led_act_n@A_LED_ACT_n#led_yellow` ×2, `led_link_n@A_LED_LINK_n#led_green` ×2.


### nic_linkwave_710da2: Linkwave LW710-DA2, dual-port 10GbE SFP+ (analog: Intel X710-DA2), x8

- **Triangles:** 4,710 in 20 meshes
- **Bounds:** min=(-0.0726, -0.0154, -0.0135) max=(0.1065, 0.0030, 0.1065) size=(0.1791, 0.0184, 0.1200)
- Frame: card (GPU frame), PCIe x8 edge 0.0560 m (x -0.0115..0.0445), board 0.1676 x 0.0689, low-profile board with a full-height bracket

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BRACKET_0` | (0.0965, -0.0069, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 | remove=-z,swap=nic_linkwave_710da2_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full |
| `A_HIT_0` | (0.0111, -0.0106, 0.0317) | +z / +y | 0.16730,0.02240,0.06340 |  |
| `A_HIT_1` | (0.101, -0.0062, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 |  |
| `A_HIT_2` | (0.0165, -0.001, -0.0028) | +z / +y | 0.05600,0.00300,0.00600 |  |
| `A_LED_ACT_0` | (0.0968, -0.0054, 0.0111) | +x / -y | 0.00200,0.00220,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_1` | (0.0968, -0.0054, 0.0509) | +x / -y | 0.00200,0.00220,0.00300 | colour=amber,fn=activity |
| `A_LED_LINK_0` | (0.0968, -0.0104, 0.0111) | +x / -y | 0.00200,0.00220,0.00300 | colour=green,fn=link |
| `A_LED_LINK_1` | (0.0968, -0.0104, 0.0509) | +x / -y | 0.00200,0.00220,0.00300 | colour=green,fn=link |
| `A_PORT_SFP_0` | (0.0965, -0.0079, 0.0215) | +x / -y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=1 |
| `A_PORT_SFP_1` | (0.0965, -0.0079, 0.0405) | +x / -y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=2 |
| `A_SCREW_PH1_0` | (0.0976, -0.0079, 0.0071) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH1_1` | (0.0976, -0.0079, 0.0549) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH2_0` | (0.1015, -0.0069, 0.1065) | +z / +x | 0.00800,0.00800,0.00800 | slot=0 |

Moving pieces: `bracket_n@A_BRACKET_n#dark_plastic`, `bracket_n@A_BRACKET_n#nickel`, `bracket_n@A_BRACKET_n#steel`, `bracket_n@A_BRACKET_n#tex_cat_server_cards`, `led_act_n@A_LED_ACT_n#led_yellow` ×2, `led_link_n@A_LED_LINK_n#led_green` ×2.


### nic_melnet_strand6_25g: Melnet Strand-6 Lx, dual-port 25GbE SFP28 (analog: NVIDIA ConnectX-6 Lx), x8

Black-anodised heatsink with the white MELNET print, SFP28 cages (`sfp=sfp28`).

- **Triangles:** 4,726 in 20 meshes
- **Bounds:** min=(-0.0726, -0.0154, -0.0135) max=(0.1065, 0.0030, 0.1065) size=(0.1791, 0.0184, 0.1200)
- Frame: card (GPU frame), PCIe x8 edge 0.0560 m (x -0.0115..0.0445), board 0.1676 x 0.0689, low-profile board with a full-height bracket

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BRACKET_0` | (0.0965, -0.0069, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 | remove=-z,swap=nic_melnet_strand6_25g_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full |
| `A_HIT_0` | (0.0111, -0.0106, 0.0317) | +z / +y | 0.16730,0.02240,0.06340 |  |
| `A_HIT_1` | (0.101, -0.0062, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 |  |
| `A_HIT_2` | (0.0165, -0.001, -0.0028) | +z / +y | 0.05600,0.00300,0.00600 |  |
| `A_LED_ACT_0` | (0.0968, -0.0054, 0.0111) | +x / -y | 0.00200,0.00220,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_1` | (0.0968, -0.0054, 0.0509) | +x / -y | 0.00200,0.00220,0.00300 | colour=amber,fn=activity |
| `A_LED_LINK_0` | (0.0968, -0.0104, 0.0111) | +x / -y | 0.00200,0.00220,0.00300 | colour=green,fn=link |
| `A_LED_LINK_1` | (0.0968, -0.0104, 0.0509) | +x / -y | 0.00200,0.00220,0.00300 | colour=green,fn=link |
| `A_PORT_SFP_0` | (0.0965, -0.0079, 0.0215) | +x / -y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp28,speed=25g,port=1 |
| `A_PORT_SFP_1` | (0.0965, -0.0079, 0.0405) | +x / -y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp28,speed=25g,port=2 |
| `A_SCREW_PH1_0` | (0.0976, -0.0079, 0.0071) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH1_1` | (0.0976, -0.0079, 0.0549) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH2_0` | (0.1015, -0.0069, 0.1065) | +z / +x | 0.00800,0.00800,0.00800 | slot=0 |

Moving pieces: `bracket_n@A_BRACKET_n#dark_plastic`, `bracket_n@A_BRACKET_n#nickel`, `bracket_n@A_BRACKET_n#steel`, `bracket_n@A_BRACKET_n#tex_cat_server_cards`, `led_act_n@A_LED_ACT_n#led_yellow` ×2, `led_link_n@A_LED_LINK_n#led_green` ×2.


### nic_melnet_strand6_100g: Melnet Strand-6 Dx, dual-port 100GbE QSFP28 (analog: ConnectX-6 Dx), x16

- **Triangles:** 5,446 in 20 meshes
- **Bounds:** min=(-0.0726, -0.0159, -0.0135) max=(0.1065, 0.0030, 0.1065) size=(0.1791, 0.0189, 0.1200)
- Frame: card (GPU frame), PCIe x16 edge 0.0890 m (x -0.0445..0.0445), board 0.1676 x 0.0689, low-profile board with a full-height bracket

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BRACKET_0` | (0.0965, -0.0069, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 | remove=-z,swap=nic_melnet_strand6_100g_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full |
| `A_HIT_0` | (0.0111, -0.0106, 0.0317) | +z / +y | 0.16730,0.02240,0.06340 |  |
| `A_HIT_1` | (0.101, -0.0062, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 |  |
| `A_HIT_2` | (-0, -0.001, -0.0028) | +z / +y | 0.08900,0.00300,0.00600 |  |
| `A_LED_ACT_0` | (0.0968, -0.0051, 0.0063) | +x / -y | 0.00200,0.00220,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_1` | (0.0968, -0.0051, 0.0567) | +x / -y | 0.00200,0.00220,0.00300 | colour=amber,fn=activity |
| `A_LED_LINK_0` | (0.0968, -0.0101, 0.0063) | +x / -y | 0.00200,0.00220,0.00300 | colour=green,fn=link |
| `A_LED_LINK_1` | (0.0968, -0.0101, 0.0567) | +x / -y | 0.00200,0.00220,0.00300 | colour=green,fn=link |
| `A_PORT_QSFP_0` | (0.0965, -0.0076, 0.019) | +x / -y | 0.01900,0.00950,0.05600 | depth=0.048,qsfp=qsfp28,speed=100g,port=1 |
| `A_PORT_QSFP_1` | (0.0965, -0.0076, 0.044) | +x / -y | 0.01900,0.00950,0.05600 | depth=0.048,qsfp=qsfp28,speed=100g,port=2 |
| `A_SCREW_PH1_0` | (0.0976, -0.0076, 0.0023) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH1_1` | (0.0976, -0.0076, 0.0607) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH2_0` | (0.1015, -0.0069, 0.1065) | +z / +x | 0.00800,0.00800,0.00800 | slot=0 |

Moving pieces: `bracket_n@A_BRACKET_n#dark_plastic`, `bracket_n@A_BRACKET_n#nickel`, `bracket_n@A_BRACKET_n#steel`, `bracket_n@A_BRACKET_n#tex_cat_server_cards`, `led_act_n@A_LED_ACT_n#led_yellow` ×2, `led_link_n@A_LED_LINK_n#led_green` ×2.


### hba_broadline_9500_16i: Broadline 9500-16i tri-mode HBA (analog: Broadcom HBA 9500-16i), x8

Two SFF-8654 x8 receptacles on the top edge, a large black finned heatsink, a vented bracket with no ports.

- **Triangles:** 5,710 in 15 meshes
- **Bounds:** min=(-0.0606, -0.0179, -0.0135) max=(0.1065, 0.0030, 0.1065) size=(0.1671, 0.0209, 0.1200)
- Frame: card (GPU frame), PCIe x8 edge 0.0560 m (x -0.0115..0.0445), board 0.1556 x 0.0689, low-profile board with a full-height bracket

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BRACKET_0` | (0.0965, -0.0069, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 | remove=-z,swap=hba_broadline_9500_16i_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full |
| `A_HIT_0` | (0.017, -0.0106, 0.0317) | +z / +y | 0.15530,0.02240,0.06340 |  |
| `A_HIT_1` | (0.101, -0.0062, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 |  |
| `A_HIT_2` | (0.0165, -0.001, -0.0028) | +z / +y | 0.05600,0.00300,0.00600 |  |
| `A_LED_SAS_0` | (-0.027, -0.0022, 0.0484) | -y / +z | 0.00200,0.00200,0.00300 | colour=green,fn=activity |
| `A_LED_SAS_1` | (0.004, -0.0022, 0.0484) | -y / +z | 0.00200,0.00200,0.00300 | colour=green,fn=activity |
| `A_PORT_SAS_0` | (-0.035, -0.0068, 0.0644) | +z / -y | 0.02950,0.01180,0.01400 | depth=0.008,conn=sff8654,lanes=8,phys=0-7,latch=+up |
| `A_PORT_SAS_1` | (-0.004, -0.0068, 0.0644) | +z / -y | 0.02950,0.01180,0.01400 | depth=0.008,conn=sff8654,lanes=8,phys=8-15,latch=+up |
| `A_SCREW_PH1_0` | (0.0976, -0.0057, 0.01) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH1_1` | (0.0976, -0.0057, 0.048) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH2_0` | (0.1015, -0.0069, 0.1065) | +z / +x | 0.00800,0.00800,0.00800 | slot=0 |

Moving pieces: `bracket_n@A_BRACKET_n#dark_plastic`, `bracket_n@A_BRACKET_n#nickel`, `bracket_n@A_BRACKET_n#steel`, `led_sas_n@A_LED_SAS_n#led_green` ×2.


### hba_broadline_9560_16i: Broadline 9560-16i RAID, 8 GB cache (analog: Broadcom MegaRAID 9560-16i + CVPM05), x8

As the HBA, plus the cache daughter board and the supercap pack on its cable.

- **Triangles:** 6,420 in 18 meshes
- **Bounds:** min=(-0.1336, -0.0179, -0.0135) max=(0.1065, 0.0030, 0.1065) size=(0.2401, 0.0209, 0.1200)
- Frame: card (GPU frame), PCIe x8 edge 0.0560 m (x -0.0115..0.0445), board 0.1556 x 0.0689, low-profile board with a full-height bracket

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BRACKET_0` | (0.0965, -0.0069, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 | remove=-z,swap=hba_broadline_9560_16i_lpbracket,screws=A_SCREW_PH1_0;A_SCREW_PH1_1,height=full |
| `A_HIT_0` | (0.017, -0.0106, 0.0317) | +z / +y | 0.15530,0.02240,0.06340 |  |
| `A_HIT_1` | (0.101, -0.0062, 0.0465) | +z / +y | 0.01100,0.01840,0.12000 |  |
| `A_HIT_2` | (0.0165, -0.001, -0.0028) | +z / +y | 0.05600,0.00300,0.00600 |  |
| `A_LED_SAS_0` | (-0.027, -0.0022, 0.0484) | -y / +z | 0.00200,0.00200,0.00300 | colour=green,fn=activity |
| `A_LED_SAS_1` | (0.004, -0.0022, 0.0484) | -y / +z | 0.00200,0.00200,0.00300 | colour=green,fn=activity |
| `A_PORT_SAS_0` | (-0.035, -0.0068, 0.0644) | +z / -y | 0.02950,0.01180,0.01400 | depth=0.008,conn=sff8654,lanes=8,phys=0-7,latch=+up |
| `A_PORT_SAS_1` | (-0.004, -0.0068, 0.0644) | +z / -y | 0.02950,0.01180,0.01400 | depth=0.008,conn=sff8654,lanes=8,phys=8-15,latch=+up |
| `A_PORT_SUPERCAP_0` | (-0.0486, -0.0046, 0.0614) | +z / -y | 0.00900,0.00600,0.00600 | depth=0.004,pins=6,plug=supercap |
| `A_SCREW_PH1_0` | (0.0976, -0.0057, 0.01) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH1_1` | (0.0976, -0.0057, 0.048) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH2_0` | (0.1015, -0.0069, 0.1065) | +z / +x | 0.00800,0.00800,0.00800 | slot=0 |
| `A_SUPERCAP_0` | (-0.1106, -0.006, 0.026) | +z / +y | 0.04600,0.01000,0.04600 | kind=supercap,cable=A_PORT_SUPERCAP_0,len=0.45,mount=chassis_clip,free=1 |

Moving pieces: `bracket_n@A_BRACKET_n#dark_plastic`, `bracket_n@A_BRACKET_n#nickel`, `bracket_n@A_BRACKET_n#steel`, `led_sas_n@A_LED_SAS_n#led_green` ×2, `supercap_n@A_SUPERCAP_n#black_plastic`, `supercap_n@A_SUPERCAP_n#dark_plastic`, `supercap_n@A_SUPERCAP_n#tex_cat_server_cards`.


### The low-profile brackets

Frame: the card's `A_BRACKET_0` pose. Same anchors for all six: `A_SCREW_PH2_0`, `A_SCREW_PH1_0..1`, `A_HIT_0`.

- **Triangles:** 900 in 4 meshes
- **Bounds:** min=(-0.0016, -0.0085, -0.0600) max=(0.0100, 0.0099, 0.0192) size=(0.0116, 0.0184, 0.0792)
- Frame: nic_linkwave_710da2's A_BRACKET_0 pose (card x 0.0965, y -0.0069, z 0.0465); tab z=0.0657, screw slot at card (x 0.1015, y -0.0069)

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_HIT_0` | (0.0043, 0.0007, -0.0204) | +z / +y | 0.01100,0.01840,0.07920 |  |
| `A_SCREW_PH1_0` | (0.0011, -0.001, -0.0394) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH1_1` | (0.0011, -0.001, 0.0084) | +x / +y | 0.00500,0.00500,0.00400 | thread=4-40,holds=bracket |
| `A_SCREW_PH2_0` | (0.005, 0, 0.0192) | +z / +x | 0.00800,0.00800,0.00800 | slot=0 |


| Model | Triangles |
|---|---|
| `nic_linkwave_350t2_lpbracket` | 564 |
| `nic_melnet_strand6_25g_lpbracket` | 900 |
| `nic_melnet_strand6_100g_lpbracket` | 900 |
| `hba_broadline_9500_16i_lpbracket` | 1,112 |
| `hba_broadline_9560_16i_lpbracket` | 1,112 |

## The rack gear

### srv_strata_sg840_4u: STRATA SG840, 4U 8-GPU server (analog: Supermicro SYS-421GE / Gigabyte G493 class)

- **Frame:** rack device, 4U; chassis 0.434 × 0.1769 × 0.700 like the existing servers (front z 0.030, rear z −0.670),
  the same ears, thumbscrews (at 2U + 22.2 mm, a rack hole), slide rails and lid.
- **Front:** eight front-loading GPU sleds `A_SLED_0..7` (numbered from +x, the viewer's left), each a perforated face
  (alpha-cut texture, so it reads opaque too) with a pull handle, a green release, the "GPU n" print and two LEDs,
  holding a passive double-width data-centre GPU (VERDIA DC 48: 267 × 111 mm, two slots, fin stack to the front, power
  connector and blind-mate connector at the back). Below them four 2.5" NVMe trays `A_BAY_0..3` (the data-centre
  tray), a vent, the badge and a front USB.
- **Inside:** the sleds' guides, the midplane with a connector per sled, a wall of ten 80 mm hot-swap fans `A_FAN_0..9`
  (two rows of five), the board with two CPU heatsinks, 16 DIMMs, three PCIe-switch heatsinks, the risers, the PSU cage
  and the power distribution board.
- **Rear:** four CRPS PSUs `A_PSU_0..3` (the data-centre PSU piece; meta `watts=3000,eff=titanium,redundancy=3+1`),
  each with `A_PORT_C14_n@A_PSU_n` and `A_LED_PSU_n@A_PSU_n`; eight vertical low-profile slot covers (one NIC per
  GPU); IPMI, two 10G RJ45, VGA, two USB, the rear ID LED; a slotted vent.

- **Triangles:** 32,460 in 205 meshes
- **Bounds:** min=(-0.2415, 0.0005, -0.7425) max=(0.2415, 0.1774, 0.0441) size=(0.4831, 0.1769, 0.7866)
- Frame: rack device, 4U, chassis 0.434 x 0.1769 x 0.700, front z=0.03, rear z=-0.670, bottom y=0.00045, top y=0.17735; 8 GPU sleds from +x, midplane z=-0.288, fan wall z=-0.320

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BAY_0..3 (4)` | (-0.1688, 0.0123, 0.03) … (0.0578, 0.0123, 0.03) | +z / +y | 0.07400,0.01900,0.10400 | pull=+z,dist=0.114,kind=sff,slot=0,latch=1 … pull=+z,dist=0.114,kind=sff,slot=3,latch=1 |
| `A_BUTTON_ID_0` | (0.2291, 0.1673, 0.0302) | +z / +y | 0.00900,0.00900,0.00600 | press=-z_local,travel=0.0010,fn=identify |
| `A_BUTTON_POWER_0` | (-0.2291, 0.1673, 0.0302) | +z / +y | 0.00980,0.00980,0.00600 | press=-z_local,travel=0.0012,fn=power,hold=4 |
| `A_FAN_0..9 (10)` | (-0.172, 0.0474, -0.32) … (0.172, 0.1315, -0.32) | +z / +y | 0.08000,0.08000,0.03800 | axis=z,spin=1,rpm=11000,hotswap=1,pull=+y … axis=z,spin=1,rpm=11000,hotswap=1,pull=+y |
| `A_HIT_0` | (-0, 0.0889, -0.32) | +z / +y | 0.43400,0.17690,0.70000 |  |
| `A_HIT_1` | (-0.2291, 0.0889, 0.015) | +z / +y | 0.02430,0.17690,0.03000 |  |
| `A_HIT_2` | (0.2291, 0.0889, 0.015) | +z / +y | 0.02430,0.17690,0.03000 |  |
| `A_LED_ACT_0` | (-0.1322, 0.0104, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_ACT_1` | (-0.1482, 0.0104, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity |
| `A_LED_DRIVEFAULT_0..3@A_BAY_0 (4)` | (-0.2024, 0.0082, 0.0303) … (0.024, 0.0082, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=amber,fn=fault … colour=amber,fn=fault |
| `A_LED_DRIVE_0..3@A_BAY_0 (4)` | (-0.2024, 0.0163, 0.0303) … (0.024, 0.0163, 0.0303) | +z / +y | 0.00200,0.00300,0.00300 | colour=green,fn=activity … colour=green,fn=activity |
| `A_LED_FAULT_0` | (0.2291, 0.1434, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=amber,fn=fault |
| `A_LED_HEALTH_0` | (0.2291, 0.1514, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=green,fn=health |
| `A_LED_ID_0` | (0.224, 0.1673, 0.0302) | +z / +y | 0.00200,0.00200,0.00300 | colour=blue,fn=identify |
| `A_LED_ID_1` | (-0.09, 0.0305, -0.6701) | -z / +y | 0.00300,0.00300,0.00300 | colour=blue,fn=identify |
| `A_LED_IPMI_0` | (-0.1095, 0.0103, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green |
| `A_LED_LINK_0` | (-0.1238, 0.0104, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_LINK_1` | (-0.1398, 0.0104, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_NET_0` | (0.2291, 0.1353, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=green,fn=network |
| `A_LED_POWER_0` | (-0.2291, 0.1673, 0.0306) | +z / +y | 0.01000,0.01000,0.00300 | colour=green,fn=power,ring=1 |
| `A_LED_PSU_0..3@A_PSU_0 (4)` | (0.171, 0.0386, -0.6712) … (-0.0531, 0.0386, -0.6712) | -z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=psu_ok … colour=green,fn=psu_ok |
| `A_LED_SLEDFAULT_0..7@A_SLED_0 (8)` | (0.158, 0.1694, 0.0303) … (-0.1955, 0.1694, 0.0303) | +z / +y | 0.00240,0.00240,0.00300 | colour=amber,fn=fault … colour=amber,fn=fault |
| `A_LED_SLED_0..7@A_SLED_0 (8)` | (0.1955, 0.1694, 0.0303) … (-0.158, 0.1694, 0.0303) | +z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=gpu_ok … colour=green,fn=gpu_ok |
| `A_LID_0` | (-0, 0.1774, -0.327) | +z / +y | 0.43400,0.00400,0.68600 | slide=-z,dist=0.020,lift=+y,latch=1 |
| `A_PORT_C14_0..3@A_PSU_0 (4)` | (0.159, 0.0267, -0.6712) … (-0.0651, 0.0267, -0.6712) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 … depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_ETH_0` | (-0.128, 0.0155, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=1 |
| `A_PORT_ETH_1` | (-0.144, 0.0155, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=2 |
| `A_PORT_IPMI_0` | (-0.105, 0.0155, -0.67) | -z / +y | 0.01600,0.01400,0.02000 | depth=0.012,rj45=1,latch=+up,net=bmc |
| `A_PORT_USBA_0` | (-0.2, 0.0115, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_USBA_1` | (-0.2, 0.0194, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_USBA_FRONT_0` | (0.2, 0.0115, 0.0295) | +z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_VGA_0` | (-0.172, 0.0155, -0.6704) | -z / +y | 0.03200,0.01300,0.01200 | depth=0.006,vga=1 |
| `A_PSU_0..3 (4)` | (0.1772, 0.0226, -0.67) … (-0.0469, 0.0226, -0.67) | +z / +y | 0.07350,0.04000,0.18500 | pull=-z,dist=0.195,watts=3000,eff=titanium,slot=0,redundancy=3+1 … pull=-z,dist=0.195,watts=3000,eff=titanium,slot=3,redundancy=3+1 |
| `A_RAIL_L_0` | (-0.221, 0.0244, -0.002) | +z / +y | 0.00800,0.04000,0.73800 | kind=slide,side=l,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_RAIL_R_0` | (0.221, 0.0244, -0.002) | +z / +y | 0.00800,0.04000,0.73800 | kind=slide,side=r,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_SCREW_THUMB_0` | (-0.2326, 0.1111, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SCREW_THUMB_1` | (0.2326, 0.1111, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SLED_0..7 (8)` | (0.1767, 0.0992, 0.03) … (-0.1767, 0.0992, 0.03) | +z / +y | 0.05010,0.15240,0.30000 | pull=+z,dist=0.310,slot=0,gpu=double_width,latch=1,blind_mate=1 … pull=+z,dist=0.310,slot=7,gpu=double_width,latch=1,blind_mate=1 |

Moving pieces: `bay_n@A_BAY_n#alu` ×4, `bay_n@A_BAY_n#black_plastic` ×4, `bay_n@A_BAY_n#dark_plastic` ×4, `bay_n@A_BAY_n#steel_dark` ×4, `bay_n@A_BAY_n#tex_parts_c_palette` ×4, `bay_n@A_BAY_n#tex_server_print` ×4, `button_id_n@A_BUTTON_ID_n#black_plastic`, `button_id_n@A_BUTTON_ID_n#grey_plastic`, `button_power_n@A_BUTTON_POWER_n#black_plastic`, `button_power_n@A_BUTTON_POWER_n#grey_plastic`, `fan_n@A_FAN_n#fan_black` ×10, `led_act_n@A_LED_ACT_n#led_yellow` ×2, `led_drive_n@A_LED_DRIVE_n@A_BAY_n#led_green` ×4, `led_drivefault_n@A_LED_DRIVEFAULT_n@A_BAY_n#led_yellow` ×4, `led_fault_n@A_LED_FAULT_n#led_yellow`, `led_health_n@A_LED_HEALTH_n#led_green`, `led_id_n@A_LED_ID_n#led_blue` ×2, `led_ipmi_n@A_LED_IPMI_n#led_green`, `led_link_n@A_LED_LINK_n#led_green` ×2, `led_net_n@A_LED_NET_n#led_green`, `led_power_n@A_LED_POWER_n#led_green`, `led_psu_n@A_LED_PSU_n@A_PSU_n#led_green` ×4, `led_sled_n@A_LED_SLED_n@A_SLED_n#led_green` ×8, `led_sledfault_n@A_LED_SLEDFAULT_n@A_SLED_n#led_yellow` ×8, `lid_n@A_LID_n#black_plastic`, `lid_n@A_LID_n#dark_plastic`, `lid_n@A_LID_n#nickel`, `lid_n@A_LID_n#steel`, `lid_n@A_LID_n#tex_server_print`, `psu_n@A_PSU_n#black_plastic` ×4, `psu_n@A_PSU_n#dark_plastic` ×4, `psu_n@A_PSU_n#fan_black` ×4, `psu_n@A_PSU_n#gold` ×4, `psu_n@A_PSU_n#nickel` ×4, `psu_n@A_PSU_n#pcb_green` ×4, `psu_n@A_PSU_n#steel` ×4, `psu_n@A_PSU_n#steel_dark` ×4, `psu_n@A_PSU_n#tex_parts_c_palette` ×4, `psu_n@A_PSU_n#tex_server_print` ×4, `rail_l_n@A_RAIL_L_n#steel`, `rail_l_n@A_RAIL_L_n#steel_dark`, `rail_r_n@A_RAIL_R_n#steel`, `rail_r_n@A_RAIL_R_n#steel_dark`, `screw_thumb_n@A_SCREW_THUMB_n#steel` ×2, `sled_n@A_SLED_n#alu` ×8, `sled_n@A_SLED_n#black_plastic` ×8, `sled_n@A_SLED_n#gold` ×8, `sled_n@A_SLED_n#paint_black` ×8, `sled_n@A_SLED_n#steel` ×8, `sled_n@A_SLED_n#tex_cat_server_rack` ×8, `sled_n@A_SLED_n#tex_cat_server_sled_mesh` ×8, `sled_n@A_SLED_n#tex_parts_c_palette` ×8.


### srv_strata_sr224_2u: STRATA SR224, 2U 24 × 2.5" storage server (analog: Dell R740xd 24 SFF)

- **Frame and rear:** the existing `server_2u` layout (`datacenter_server.layout("server_2u")`): chassis, rear I/O,
  slot covers, two PSUs, the interior (board, CPUs, DIMMs, six 60 mm fans, shroud, risers), the lid and the rails.
- **Front:** 24 vertical hot-swap trays `A_BAY_0..23` (`orient=vertical`, numbered from +x), each with the vented
  top, two LEDs (`A_LED_DRIVE_n@A_BAY_n`, `A_LED_DRIVEFAULT_n@A_BAY_n`), the lever with ribs, the green release and the
  2.5" drive with its label; the cage tunnels and the backplane with a connector per bay; the badges in the band above.
  No bezel (the 2U data-centre server's bezel prints its own model name).

- **Triangles:** 24,602 in 244 meshes
- **Bounds:** min=(-0.2415, 0.0008, -0.7425) max=(0.2415, 0.0882, 0.0367) size=(0.4831, 0.0874, 0.7792)
- Frame: rack device, 2U, chassis 0.434 x 0.0873 x 0.700, front z=0.03, rear z=-0.670, bottom y=0.00080, top y=0.08810; 24 vertical 2.5" bays numbered from +x

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BAY_0..23 (24)` | (0.2041, 0.0406, 0.03) … (-0.2041, 0.0406, 0.03) | +z / +y | 0.01735,0.07600,0.10400 | pull=+z,dist=0.114,kind=sff,slot=0,latch=1,orient=vertical … pull=+z,dist=0.114,kind=sff,slot=23,latch=1,orient=vertical |
| `A_BUTTON_ID_0` | (0.2291, 0.0781, 0.0302) | +z / +y | 0.00900,0.00900,0.00600 | press=-z_local,travel=0.0010,fn=identify |
| `A_BUTTON_POWER_0` | (-0.2291, 0.0781, 0.0302) | +z / +y | 0.00980,0.00980,0.00600 | press=-z_local,travel=0.0012,fn=power,hold=4 |
| `A_FAN_0..5 (6)` | (-0.1683, 0.0322, -0.134) … (0.1683, 0.0322, -0.134) | +z / +y | 0.06000,0.06000,0.03800 | axis=z,spin=1,rpm=6500,hotswap=1,pull=+y … axis=z,spin=1,rpm=6500,hotswap=1,pull=+y |
| `A_HIT_0` | (-0, 0.0445, -0.32) | +z / +y | 0.43400,0.08730,0.70000 |  |
| `A_HIT_1` | (-0.2291, 0.0445, 0.015) | +z / +y | 0.02430,0.08730,0.03000 |  |
| `A_HIT_2` | (0.2291, 0.0445, 0.015) | +z / +y | 0.02430,0.08730,0.03000 |  |
| `A_LED_ACT_0..3 (4)` | (-0.0182, 0.0098, -0.6701) … (0.0298, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=amber,fn=activity … colour=amber,fn=activity |
| `A_LED_DRIVEFAULT_0..23@A_BAY_0 (24)` | (0.2076, 0.0736, 0.0303) … (-0.2006, 0.0736, 0.0303) | +z / +y | 0.00240,0.00200,0.00300 | colour=amber,fn=fault … colour=amber,fn=fault |
| `A_LED_DRIVE_0..23@A_BAY_0 (24)` | (0.2006, 0.0736, 0.0303) … (-0.2076, 0.0736, 0.0303) | +z / +y | 0.00240,0.00200,0.00300 | colour=green,fn=activity … colour=green,fn=activity |
| `A_LED_FAULT_0` | (0.2291, 0.0541, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=amber,fn=fault |
| `A_LED_HEALTH_0` | (0.2291, 0.0621, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=green,fn=health |
| `A_LED_ID_0` | (0.224, 0.0781, 0.0302) | +z / +y | 0.00200,0.00200,0.00300 | colour=blue,fn=identify |
| `A_LED_ID_1` | (0.05, 0.0308, -0.6701) | -z / +y | 0.00300,0.00300,0.00300 | colour=blue,fn=identify |
| `A_LED_IPMI_0` | (-0.1025, 0.0096, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green |
| `A_LED_LINK_0..3 (4)` | (-0.0098, 0.0098, -0.6701) … (0.0382, 0.0098, -0.6701) | -z / +y | 0.00220,0.00200,0.00300 | colour=green,fn=link … colour=green,fn=link |
| `A_LED_NET_0` | (0.2291, 0.0461, 0.0302) | +z / +y | 0.00260,0.00200,0.00300 | colour=green,fn=network |
| `A_LED_POWER_0` | (-0.2291, 0.0781, 0.0306) | +z / +y | 0.01000,0.01000,0.00300 | colour=green,fn=power,ring=1 |
| `A_LED_PSU_0@A_PSU_0` | (0.171, 0.039, -0.6712) | -z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=psu_ok |
| `A_LED_PSU_1@A_PSU_1` | (-0.1835, 0.039, -0.6712) | -z / +y | 0.00240,0.00240,0.00300 | colour=green,fn=psu_ok |
| `A_LID_0` | (-0, 0.0881, -0.327) | +z / +y | 0.43400,0.00400,0.68600 | slide=-z,dist=0.020,lift=+y,latch=1 |
| `A_PORT_C14_0@A_PSU_0` | (0.159, 0.027, -0.6712) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_C14_1@A_PSU_1` | (-0.1955, 0.027, -0.6712) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_ETH_0..3 (4)` | (-0.014, 0.0148, -0.67) … (0.034, 0.0148, -0.67) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=10g,lom=1 … depth=0.012,rj45=1,latch=+up,speed=10g,lom=4 |
| `A_PORT_IPMI_0` | (-0.098, 0.0148, -0.67) | -z / +y | 0.01600,0.01400,0.02000 | depth=0.012,rj45=1,latch=+up,net=bmc |
| `A_PORT_USBA_0` | (-0.04, 0.0108, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_USBA_1` | (-0.04, 0.0188, -0.67) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=3.0 |
| `A_PORT_VGA_0` | (-0.068, 0.0148, -0.6704) | -z / +y | 0.03200,0.01300,0.01200 | depth=0.006,vga=1 |
| `A_PSU_0` | (0.1772, 0.023, -0.67) | +z / +y | 0.07350,0.04000,0.18500 | pull=-z,dist=0.195,watts=800,eff=platinum,slot=0 |
| `A_PSU_1` | (-0.1772, 0.023, -0.67) | +z / +y | 0.07350,0.04000,0.18500 | pull=-z,dist=0.195,watts=800,eff=platinum,slot=1 |
| `A_RAIL_L_0` | (-0.221, 0.0248, -0.002) | +z / +y | 0.00800,0.04000,0.73800 | kind=slide,side=l,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_RAIL_R_0` | (0.221, 0.0248, -0.002) | +z / +y | 0.00800,0.04000,0.73800 | kind=slide,side=r,front=0,rear=-0.74,len=0.738,extend=+z,travel=0.62 |
| `A_SCREW_THUMB_0` | (-0.2326, 0.0381, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SCREW_THUMB_1` | (0.2326, 0.0381, 0.03) | +z / +y | 0.01200,0.01200,0.01200 | thread=M6,captive=1,len=0.032,turns=4 |
| `A_SHROUD_0` | (-0, 0.0739, -0.3075) | +z / +y | 0.40000,0.00600,0.16000 | lift=+y,dist=0.06,order=1 |

Moving pieces: `bay_n@A_BAY_n#alu` ×24, `bay_n@A_BAY_n#black_plastic` ×24, `bay_n@A_BAY_n#dark_plastic` ×24, `bay_n@A_BAY_n#tex_cat_server_rack` ×24, `bay_n@A_BAY_n#tex_parts_c_palette` ×24, `button_id_n@A_BUTTON_ID_n#black_plastic`, `button_id_n@A_BUTTON_ID_n#grey_plastic`, `button_power_n@A_BUTTON_POWER_n#black_plastic`, `button_power_n@A_BUTTON_POWER_n#grey_plastic`, `fan_n@A_FAN_n#fan_black` ×6, `led_act_n@A_LED_ACT_n#led_yellow` ×4, `led_drive_n@A_LED_DRIVE_n@A_BAY_n#led_green` ×24, `led_drivefault_n@A_LED_DRIVEFAULT_n@A_BAY_n#led_yellow` ×24, `led_fault_n@A_LED_FAULT_n#led_yellow`, `led_health_n@A_LED_HEALTH_n#led_green`, `led_id_n@A_LED_ID_n#led_blue` ×2, `led_ipmi_n@A_LED_IPMI_n#led_green`, `led_link_n@A_LED_LINK_n#led_green` ×4, `led_net_n@A_LED_NET_n#led_green`, `led_power_n@A_LED_POWER_n#led_green`, `led_psu_n@A_LED_PSU_n@A_PSU_n#led_green` ×2, `lid_n@A_LID_n#black_plastic`, `lid_n@A_LID_n#dark_plastic`, `lid_n@A_LID_n#nickel`, `lid_n@A_LID_n#steel`, `lid_n@A_LID_n#tex_server_print`, `psu_n@A_PSU_n#black_plastic` ×2, `psu_n@A_PSU_n#dark_plastic` ×2, `psu_n@A_PSU_n#fan_black` ×2, `psu_n@A_PSU_n#gold` ×2, `psu_n@A_PSU_n#nickel` ×2, `psu_n@A_PSU_n#pcb_green` ×2, `psu_n@A_PSU_n#steel` ×2, `psu_n@A_PSU_n#steel_dark` ×2, `psu_n@A_PSU_n#tex_parts_c_palette` ×2, `psu_n@A_PSU_n#tex_server_print` ×2, `rail_l_n@A_RAIL_L_n#steel`, `rail_l_n@A_RAIL_L_n#steel_dark`, `rail_r_n@A_RAIL_R_n#steel`, `rail_r_n@A_RAIL_R_n#steel_dark`, `screw_thumb_n@A_SCREW_THUMB_n#steel` ×2, `shroud_n@A_SHROUD_n#black_plastic`, `shroud_n@A_SHROUD_n#tex_server_print`.


### srv_linkwave_ls4804x: LINKWAVE LS-4804X, 48 × 1GbE + 4 × SFP+ (analog: Cisco CBS350-48T-4X)

- **Frame:** rack device, 1U, body 0.440 × 0.0436 × 0.280, front face z 0.0045, ears with `A_SCREW_RACK_0..3`.
- **Front** (+x is the viewer's left): logo, `A_LED_POWER_0` / `SYS_0` / `FAN_0`, a reset pinhole, four 2 × 6 RJ45
  blocks (`datacenter_net.rj45_bank`): `A_PORT_ETH_0..47` is port n+1, odd ports on top (latch up), even below
  (latch down), +Y towards the latch, each with `A_LED_LINK_n` / `A_LED_ACT_n` and its printed number; then four SFP+
  cages `A_PORT_SFP_0..3` (ports 49–52) with `A_LED_SFP_n`.
- **Rear:** `A_PORT_C14_0`, the console `A_PORT_CONSOLE_0` and out-of-band `A_PORT_MGMT_0` (RJ45), `A_PORT_USBA_0`,
  three 40 mm fans `A_FAN_0..2`, an earth screw. The rating label on the top.

- **Triangles:** 18,958 in 113 meshes
- **Bounds:** min=(-0.2413, 0.0004, -0.2790) max=(0.2413, 0.0441, 0.0051) size=(0.4826, 0.0437, 0.2841)
- Frame: rack device, 1U, body 0.440 x 0.0436 x 0.280, front z=0.0045, rear z=-0.2755

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_FAN_0` | (0.03, 0.0222, -0.2595) | -z / +y | 0.04000,0.04000,0.02000 | axis=z,spin=1,rpm=7000 |
| `A_FAN_1` | (0.09, 0.0222, -0.2595) | -z / +y | 0.04000,0.04000,0.02000 | axis=z,spin=1,rpm=7000 |
| `A_FAN_2` | (0.15, 0.0222, -0.2595) | -z / +y | 0.04000,0.04000,0.02000 | axis=z,spin=1,rpm=7000 |
| `A_HIT_0` | (-0, 0.0222, -0.1355) | +z / +y | 0.44000,0.04360,0.28000 |  |
| `A_HIT_1` | (-0, 0.0222, 0.001) | +z / +y | 0.48260,0.04360,0.00400 |  |
| `A_LED_ACT_0..47 (48)` | (0.1721, 0.0365, 0.0048) … (-0.1683, 0.0087, 0.0048) | +z / +y | 0.00200,0.00200,0.00300 | colour=amber,fn=activity … colour=amber,fn=activity |
| `A_LED_FAN_0` | (0.191, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=amber,fn=fan |
| `A_LED_LINK_0..47 (48)` | (0.1811, 0.0365, 0.0048) … (-0.1593, 0.0087, 0.0048) | +z / +y | 0.00200,0.00200,0.00300 | colour=green,fn=link … colour=green,fn=link |
| `A_LED_POWER_0` | (0.211, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=power |
| `A_LED_SFP_0..3 (4)` | (-0.1843, 0.0376, 0.0048) … (-0.2008, 0.0076, 0.0048) | +z / +y | 0.00300,0.00200,0.00300 | colour=green,fn=link … colour=green,fn=link |
| `A_LED_SYS_0` | (0.201, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=sys |
| `A_PORT_C14_0` | (-0.17, 0.0224, -0.2755) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14,psu=1 |
| `A_PORT_CONSOLE_0` | (-0.12, 0.0224, -0.2755) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,serial=rs232,baud=115200 |
| `A_PORT_ETH_0..47 (48)` | (0.1766, 0.0311, 0.0045) … (-0.1638, 0.0141, 0.0045) | +z / +y | 0.01420,0.01250,0.02000 | depth=0.012,rj45=1,latch=+up,port=1,speed=1g,poe=0 … depth=0.012,rj45=1,latch=+up,port=48,speed=1g,poe=0 |
| `A_PORT_MGMT_0` | (-0.1, 0.0224, -0.2755) | -z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=1g,net=oob |
| `A_PORT_SFP_0..3 (4)` | (-0.1843, 0.0311, 0.0045) … (-0.2008, 0.0141, 0.0045) | +z / +y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=49 … depth=0.042,sfp=sfp+,speed=10g,port=52 |
| `A_PORT_USBA_0` | (-0.08, 0.0224, -0.2755) | -z / +y | 0.01450,0.00720,0.02000 | depth=0.009,usb=2.0,fn=config |
| `A_SCREW_RACK_0..3 (4)` | (-0.2326, 0.0063, 0.002) … (0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l … thread=M6,cage=1,side=r |

Moving pieces: `fan_n@A_FAN_n#fan_black` ×3, `led_act_n@A_LED_ACT_n#led_yellow` ×48, `led_fan_n@A_LED_FAN_n#led_yellow`, `led_link_n@A_LED_LINK_n#led_green` ×48, `led_power_n@A_LED_POWER_n#led_green`, `led_sfp_n@A_LED_SFP_n#led_green` ×4, `led_sys_n@A_LED_SYS_n#led_green`.


### srv_linkwave_ls1600x: LINKWAVE LS-1600X, 16 × 10G SFP+ aggregation (analog: MikroTik CRS317-1G-16S+RM)

- **Front:** two blocks of 2 × 4 SFP+ cages `A_PORT_SFP_0..15` (port n+1; odd ports on top; +Y towards the latch,
  `latch=+up`), each with `A_LED_LINK_n` / `A_LED_ACT_n`; `A_PORT_MGMT_0` (1G RJ45, `A_LED_MGMT_0`) and
  `A_PORT_CONSOLE_0`; status LEDs including `A_LED_PSU_0/1`; a vent.
- **Rear:** two C14 inlets `A_PORT_C14_0/1` (two PSUs), four 40 mm fans `A_FAN_0..3`.

- **Triangles:** 14,024 in 49 meshes
- **Bounds:** min=(-0.2413, 0.0004, -0.2990) max=(0.2413, 0.0441, 0.0051) size=(0.4826, 0.0437, 0.3041)
- Frame: rack device, 1U, body 0.440 x 0.0436 x 0.300, front z=0.0045, rear z=-0.2955

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_FAN_0..3 (4)` | (-0, 0.0222, -0.2795) … (0.18, 0.0222, -0.2795) | -z / +y | 0.04000,0.04000,0.02000 | axis=z,spin=1,rpm=7000 … axis=z,spin=1,rpm=7000 |
| `A_HIT_0` | (-0, 0.0222, -0.1455) | +z / +y | 0.44000,0.04360,0.30000 |  |
| `A_HIT_1` | (-0, 0.0222, 0.001) | +z / +y | 0.48260,0.04360,0.00400 |  |
| `A_LED_ACT_0..15 (16)` | (0.1177, 0.0376, 0.0048) … (-0.0548, 0.0076, 0.0048) | +z / +y | 0.00300,0.00200,0.00300 | colour=amber,fn=activity … colour=amber,fn=activity |
| `A_LED_FAN_0` | (0.176, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=amber,fn=fan |
| `A_LED_LINK_0..15 (16)` | (0.1247, 0.0376, 0.0048) … (-0.0478, 0.0076, 0.0048) | +z / +y | 0.00300,0.00200,0.00300 | colour=green,fn=link … colour=green,fn=link |
| `A_LED_MGMT_0` | (-0.1155, 0.0195, 0.0048) | +z / +y | 0.00200,0.00200,0.00300 | colour=green,fn=link |
| `A_LED_POWER_0` | (0.201, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=power |
| `A_LED_PSU_0` | (0.1635, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=psu1 |
| `A_LED_PSU_1` | (0.153, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=psu2 |
| `A_LED_SYS_0` | (0.1885, 0.0134, 0.0048) | +z / +y | 0.00260,0.00260,0.00300 | colour=green,fn=sys |
| `A_PORT_C14_0` | (-0.17, 0.0224, -0.2955) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14,psu=1 |
| `A_PORT_C14_1` | (-0.12, 0.0224, -0.2955) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14,psu=2 |
| `A_PORT_CONSOLE_0` | (-0.14, 0.0141, 0.0045) | +z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,serial=rs232,baud=115200 |
| `A_PORT_MGMT_0` | (-0.12, 0.0141, 0.0045) | +z / +y | 0.01450,0.01200,0.02000 | depth=0.012,rj45=1,latch=+up,speed=1g,net=oob |
| `A_PORT_SFP_0..15 (16)` | (0.1212, 0.0311, 0.0045) … (-0.0512, 0.0141, 0.0045) | +z / +y | 0.01450,0.01050,0.05000 | depth=0.042,sfp=sfp+,speed=10g,port=1,latch=+up … depth=0.042,sfp=sfp+,speed=10g,port=16,latch=+up |
| `A_SCREW_RACK_0..3 (4)` | (-0.2326, 0.0063, 0.002) … (0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l … thread=M6,cage=1,side=r |

Moving pieces: `fan_n@A_FAN_n#fan_black` ×4, `led_act_n@A_LED_ACT_n#led_yellow` ×16, `led_fan_n@A_LED_FAN_n#led_yellow`, `led_link_n@A_LED_LINK_n#led_green` ×16, `led_mgmt_n@A_LED_MGMT_n#led_green`, `led_power_n@A_LED_POWER_n#led_green`, `led_psu_n@A_LED_PSU_n#led_green` ×2, `led_sys_n@A_LED_SYS_n#led_green`.


### srv_strata_shelf_1u: 1U cantilever shelf

A front-mount steel shelf: the 1U front plate is its own pair of ears (`A_SCREW_RACK_0..3`), a 400 mm vented tray with
20 mm side lips and a rear lip, gussets, rubber strips and the load label. `A_SHELF_0` is the load surface.

- **Triangles:** 2,724 in 3 meshes
- **Bounds:** min=(-0.2413, 0.0004, -0.4000) max=(0.2413, 0.0441, 0.0021) size=(0.4826, 0.0437, 0.4021)
- Frame: rack device, 1U front-mount shelf, panel face z=0.002, tray top y=0.0019, depth 0.4

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_HIT_0` | (-0, 0.0104, -0.2) | +z / +y | 0.44400,0.02000,0.40000 |  |
| `A_HIT_1` | (-0, 0.0222, 0.001) | +z / +y | 0.48260,0.04365,0.00400 |  |
| `A_SCREW_RACK_0..3 (4)` | (-0.2326, 0.0063, 0.002) … (0.2326, 0.0381, 0.002) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l … thread=M6,cage=1,side=r |
| `A_SHELF_0` | (-0, 0.0027, -0.2) | +y / -z | 0.44000,0.39600,0.00400 | surface=1,w=0.440,d=0.396,load_kg=25,front_mount=1 |


### srv_strata_blank_1u and srv_strata_blank_2u: blanking panels

1.2 mm steel, black, flanges bent back 12 mm, pressed ribs, a faint STRATA print; the M6 screws and cup washers are
fitted (`A_SCREW_RACK_n` carry them as moving pieces, meta `fitted=1`), at the bottom and top holes of the panel.

- **Triangles:** 1,502 in 14 meshes
- **Bounds:** min=(-0.2413, 0.0001, -0.0120) max=(0.2413, 0.0443, 0.0058) size=(0.4826, 0.0442, 0.0178)
- Frame: rack device, 1U blanking panel, face z=0.0012, flanges to z=-0.012

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_HIT_0` | (-0, 0.0222, -0.004) | +z / +y | 0.48260,0.04365,0.01600 |  |
| `A_SCREW_RACK_0..3 (4)` | (-0.2326, 0.0063, 0.0012) … (0.2326, 0.0381, 0.0012) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l,fitted=1 … thread=M6,cage=1,side=r,fitted=1 |

Moving pieces: `screw_rack_n@A_SCREW_RACK_n#black_plastic` ×4, `screw_rack_n@A_SCREW_RACK_n#dark_plastic` ×4, `screw_rack_n@A_SCREW_RACK_n#nickel` ×4.


- **Triangles:** 1,590 in 14 meshes
- **Bounds:** min=(-0.2413, 0.0001, -0.0120) max=(0.2413, 0.0888, 0.0058) size=(0.4826, 0.0886, 0.0178)
- Frame: rack device, 2U blanking panel, face z=0.0012, flanges to z=-0.012

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_HIT_0` | (-0, 0.0445, -0.004) | +z / +y | 0.48260,0.08810,0.01600 |  |
| `A_SCREW_RACK_0..3 (4)` | (-0.2326, 0.0063, 0.0012) … (0.2326, 0.0825, 0.0012) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l,fitted=1 … thread=M6,cage=1,side=r,fitted=1 |

Moving pieces: `screw_rack_n@A_SCREW_RACK_n#black_plastic` ×4, `screw_rack_n@A_SCREW_RACK_n#dark_plastic` ×4, `screw_rack_n@A_SCREW_RACK_n#nickel` ×4.


### srv_strata_cma: cable management arm for the 1U server rails

Two black U-channel arms with wire cable hoops and hook-and-loop straps, a hinged elbow and green release tabs; it fits
the STRATA slide rails of `server_1u` (rail centre y 0.0194). See the contract above.

- **Triangles:** 2,750 in 13 meshes
- **Bounds:** min=(-0.2234, 0.0005, -0.7985) max=(0.2234, 0.0383, -0.6520) size=(0.4468, 0.0379, 0.1465)
- Frame: rack device (the frame of the server it serves, installed at the same A_RACKU_n); outer rail rear end z=-0.7385, inner rail rear end z=-0.66, rail centre y=0.0194

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_ARM_0` | (0.214, 0.0194, -0.7565) | +z / +y | 0.42000,0.03200,0.02000 | hinge=y,closed=0,open=80,follows=A_RAIL_R_0,travel=0.62 |
| `A_ARM_1@A_ARM_0` | (-0.206, 0.0194, -0.7298) | +z / +y | 0.42000,0.03200,0.02000 | hinge=y,closed=0,open=-160,follows=A_ARM_0 |
| `A_HIT_0` | (-0, 0.0194, -0.7298) | +z / +y | 0.44800,0.03600,0.07150 |  |
| `A_MOUNT_INNER_0@A_ARM_1@A_ARM_0` | (0.2195, 0.0194, -0.66) | +z / +y | 0.00400,0.01600,0.02000 | clip=inner_rail,side=r,insert=+z,release=green_tab |
| `A_MOUNT_OUTER_0` | (0.2215, 0.0194, -0.72) | +z / +y | 0.00600,0.02600,0.02000 | clip=outer_rail,side=r,insert=+z,release=green_tab |
| `A_MOUNT_SUPPORT_0` | (-0.2215, 0.0194, -0.72) | +z / +y | 0.00600,0.02600,0.02000 | clip=outer_rail,side=l,insert=+z,release=green_tab |

Moving pieces: `arm_n@A_ARM_n#black_plastic`, `arm_n@A_ARM_n#nickel`, `arm_n@A_ARM_n#paint_black`, `arm_n@A_ARM_n#steel`, `arm_n@A_ARM_n#tex_cat_server_rack`, `arm_n@A_ARM_n@A_ARM_n#black_plastic`, `arm_n@A_ARM_n@A_ARM_n#nickel`, `arm_n@A_ARM_n@A_ARM_n#paint_black`, `arm_n@A_ARM_n@A_ARM_n#steel`, `arm_n@A_ARM_n@A_ARM_n#steel_dark`, `arm_n@A_ARM_n@A_ARM_n#tex_parts_c_palette`.


### srv_strata_kvm_1u: STRATA KMM 18.5" 1U console drawer (analog: Dell DKMMLED185)

- **Fixed:** the outer slides with their front ears (`A_SCREW_RACK_0..3`) and rear brackets on the rear rails
  (`A_SCREW_RACK_4..7`, meta `rear=1`), the electronics box with `A_PORT_VGA_0`, `A_PORT_USBB_0` and `A_PORT_C14_0`.
- **Drawer** `A_DRAWER_0`: the front panel with the handle bar, the green release tabs, the badge, the LCD button and
  power LED; a full keyboard (individual caps with one legend overlay) and a touchpad; the rear box and the hinges; the
  lid `A_LID_0@A_DRAWER_0` with `A_SCREEN_0` (18.5", 0.410 × 0.231, `ref=1366x768`). Preview 4–5 show it pulled out
  0.40 m with the lid open at −105°.

- **Triangles:** 6,662 in 22 meshes
- **Bounds:** min=(-0.2440, 0.0007, -0.7385) max=(0.2440, 0.0437, 0.0467) size=(0.4880, 0.0430, 0.7852)
- Frame: rack device, 1U, drawer front z=0.02, drawer 0.52 long, electronics box to z=-0.6, slides to z=-0.74

| Anchor | Position | Fwd / up | Size | Meta |
|---|---|---|---|---|
| `A_BUTTON_LCD_0@A_DRAWER_0` | (0.09, 0.0304, 0.0202) | +z / +y | 0.00900,0.00900,0.00600 | press=-z_local,travel=0.0010,fn=lcd_power |
| `A_DRAWER_0` | (-0, 0.0224, 0.02) | +z / +y | 0.43600,0.04360,0.52000 | pull=+z,dist=0.450,latch=front_tabs,stop=1 |
| `A_HIT_0` | (-0, 0.0222, -0.29) | +z / +y | 0.43600,0.04360,0.62000 |  |
| `A_HIT_1` | (-0, 0.0222, 0.001) | +z / +y | 0.48260,0.04360,0.00400 |  |
| `A_LED_POWER_0@A_DRAWER_0` | (0.082, 0.0304, 0.0202) | +z / +y | 0.00220,0.00220,0.00300 | colour=green,fn=power |
| `A_LID_0@A_DRAWER_0` | (-0, 0.0314, -0.246) | +z / +y | 0.43200,0.01650,0.26200 | hinge=x,open=-105,min=-115,max=0,closed=0 |
| `A_PORT_C14_0` | (0.12, 0.0164, -0.601) | -z / +y | 0.02800,0.02000,0.01200 | depth=0.008,plug=c13,inlet=c14 |
| `A_PORT_USBB_0` | (-0.085, 0.0164, -0.6) | -z / +y | 0.01200,0.01200,0.01200 | depth=0.008,usb=b,fn=keyboard_mouse |
| `A_PORT_VGA_0` | (-0.12, 0.0164, -0.6004) | -z / +y | 0.03200,0.01300,0.01200 | depth=0.006,vga=1,fn=video_in |
| `A_SCREEN_0@A_LID_0@A_DRAWER_0` | (-0, 0.0233, -0.112) | -y / +z | 0.41000,0.23100,0.00300 | kind=lcd,ref=1366x768,diag=18.5,colour=rgb |
| `A_SCREW_RACK_0..7 (8)` | (-0.2326, 0.0063, 0.002) … (0.2326, 0.0381, -0.7365) | +z / +y | 0.01200,0.01000,0.00600 | thread=M6,cage=1,side=l … thread=M6,cage=1,side=r,rear=1 |

Moving pieces: `button_lcd_n@A_BUTTON_LCD_n@A_DRAWER_n#black_plastic`, `drawer_n@A_DRAWER_n#alu`, `drawer_n@A_DRAWER_n#black_plastic`, `drawer_n@A_DRAWER_n#dark_plastic`, `drawer_n@A_DRAWER_n#grey_plastic`, `drawer_n@A_DRAWER_n#paint_black`, `drawer_n@A_DRAWER_n#steel`, `drawer_n@A_DRAWER_n#steel_dark`, `drawer_n@A_DRAWER_n#tex_cat_server_rack`, `drawer_n@A_DRAWER_n#tex_parts_c_palette`, `led_power_n@A_LED_POWER_n@A_DRAWER_n#led_green`, `lid_n@A_LID_n@A_DRAWER_n#black_plastic`, `lid_n@A_LID_n@A_DRAWER_n#dark_plastic`, `lid_n@A_LID_n@A_DRAWER_n#paint_black`, `screen_n@A_SCREEN_n@A_LID_n@A_DRAWER_n#tex_cat_server_rack`.


## Deviations and notes

- **Names:** the real series words are replaced (ConnectX → "Strand", MegaRAID → none, CacheVault → "CacheGuard",
  PowerEdge → none); the numbering is kept (X710 → LW710-DA2, 9500-16i, 9560-16i). The GPUs in the sleds are an
  unbranded-in-the-catalogue "VERDIA DC 48" (the GPU family's data-centre accelerator is task 11's).
- **Cards are low profile** (68.9 mm) with a full-height bracket, as the real ones ship; that is what makes the
  low-profile bracket swap meaningful. They are single-slot, so only `A_SCREW_PH2_0` exists (no `_1`).
- **SFP / QSFP LEDs** are light pipes in the bracket beside the cages (the real cards' arrangement); there is no
  separate `A_LED_SFP_n` on the cards, only `A_LED_LINK_n` / `A_LED_ACT_n`, the same names as the RJ45 card.
- **PSU label:** the 4U server's PSUs are the data-centre CRPS piece, whose label (in the shared `server_print.png`)
  says 800 W; their anchor meta says `watts=3000`. The label sits on the PSU's top, out of sight when installed.
- **Triangle budget:** task 01 kept its 1U/2U servers and the switch under 25k. `srv_strata_sr224_2u` (24 trays) and
  the switches are inside it; the 4U GPU server is about 32k (eight complete GPU sleds and ten 80 mm fans) — under the
  racks' 40k.
- **Cable arm:** it fits the 1U STRATA rails only (its arms are sized for 1U and its connectors sit at the 1U rail
  height); the 2U and 4U servers' rails sit 5.4 mm higher.
- **The KVM screen** quad carries the console art from `cat_server_rack.png` (so the previews show a working console);
  the game drives `A_SCREEN_0` itself and may replace that material.
- **Ports of the 48-port switch** at the rear (console, management, USB): the front has no room left after 48 RJ45 and
  4 SFP+ cages on a 440 mm panel.
- **No hooks** were added to `build_datacenter.py`, so no data-centre model was re-exported; `datacenter_fit.py` is
  unchanged (its functions are imported by `cat_server_fit.py`).

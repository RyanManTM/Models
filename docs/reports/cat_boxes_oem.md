# Catalogue 19, boxes: the server / OEM group

Brief: `docs/tasks/catalog/19-boxes.md` ("server parts"). The coordinator folds this into `docs/reports/cat_boxes.md`
and writes `box` / `box_size` into the catalogue JSON (not done here).

## Status
**14 of 24 boxes built.** Done: cpu_epoch_9124, cpu_epoch_9354, cpu_epoch_9654, cpu_tiron_plat_8480, ram_kingsland_rdimm5_32, ram_sorin_rdimm5_64, ram_crux_rdimm5_128, ram_kingsland_rdimm4_32, ssd_sorin_pm9a3_3840, ssd_sorin_pm9a3_7680, cooler_srv_epoch_1u, cooler_srv_platinum_2u, psu_strata_crps_800, psu_strata_crps_1600. Not built yet: nic_linkwave_350t2, nic_linkwave_710da2, nic_melnet_strand6_25g, nic_melnet_strand6_100g, hba_broadline_9500_16i, hba_broadline_9560_16i, gpu_verdia_t100, gpu_voltra_mi210, mb_strata_spv, mb_strata_l46.

## What was made
- **`Tools/Blender/rig_oem.py`** (new rig module, listed in `build_boxes.RIG_MODULES`): the builders of the kinds
  `oem_cpu`, `oem_rdimm`, `oem_u2`, `oem_heatsink`, `oem_psu`, `oem_card` and `oem_board`, their `SIZE` (every box sized
  from the part's measured bounds, 5 mm steps), their `ART` and the `item()` hook.
- Per box: `Assets/Resources/Models/box_<id>.fbx`, `Textures/box_<id>.png` (the OEM print atlas),
  `Textures/box_<id>_in.png` (the inner print; the OEM rigs only use its swatches), previews
  `Logs/ModelPreviews/box_<id>_0..3.png` (closed front, closed back, opened with the contents in place, exploded) and
  `box_<id>_report.txt` (meshes and anchors).

## The print (`item()` and `ART`)
- `item()` sets `style="oem"`, `oem_base="white"` (the board carton `"kraft"`) and writes the words from each part's
  specs: `line` (SERVER PROCESSOR, SERVER MEMORY, ENTERPRISE NVMe SSD, SERVER CPU HEATSINK, CRPS HOT-PLUG POWER SUPPLY,
  NETWORK ADAPTER, HOST BUS ADAPTER / RAID CONTROLLER, DATA CENTRE ACCELERATOR, SERVER MOTHERBOARD), a `label_line`
  for the label's brand bar (SOCKET SP-V PROCESSOR, DDR5 RDIMM ECC, U.2 NVMe SSD, 1600 W CRPS PSU, ...), up to 6
  `specs` and the `bag` of the part. Cards with a low-profile bracket list it in `acc_models`, so the driver
  measures it.
- `ART` = `oem_art`: `build_boxes.compose_oem` with the product label where it is seen: on the front and the right
  end of a tall box, on the top of a flat one (box height < half its smaller footprint side: CPU, RDIMM, card, board
  cartons). Every side carries the brand in one ink and the label line; the top the brand. The label is
  `build_boxes.oem_label` (brand sticker bar, name, P/N, bar code, S/N, QTY 1, ESD mark).

## The rig designs (one per size class, scaled to the part)
All rigs: origin at the bottom centre, +z the front, y up, closed pose, `A_HIT_0` = the outer size. Every paper of
the part's `docs` list is one `A_ITEM_DOC_n` (`rig_products.paper_list`, in a pile whose top paper comes out first,
each one `under` the one above it). The part's own caps, guards and films stay on the part (its `unbox` entry).

### Small: server CPU (`oem_cpu`)
A white tuck-top carton (`rig_products.tuck_walls`, `tuck_lid_top`, `dust_flaps`, thumb notch in the front wall), two
round clear seals over the lid's front edge. Inside, a black PE foam pad with a die-cut window; the clamshell tray
(`rig_products.clamshell`: black moulded base with a ledge and a pocket, a **clear** hinged lid so the carrier shows)
sits in the window, parented to the pad, so the pad lifts out with the clamshell. The CPU lies pads down on the
ledge, in its carrier (`A_CARRIER_0` is part of the CPU model; the Arc Epoch carrier is orange, the Tiron Platinum one
black), its contact cover cap on the pads (on the part), `bag=none`. The papers lie on the clamshell lid.
Size: the clamshell flange (the part's footprint + 26 mm) + 10 mm, 30 mm tall.

### Small: RDIMM (`oem_rdimm`)
A white end-tuck carton (`rig_products.end_tuck_box`) with a round seal over the end flap's top edge. A clear
clamshell (`rig_products.blister`, one cavity) slides out along +x; the module lies in it label side up, gold fingers
to the front, in its pink anti-static bag (`bag=antistatic_pink`, `guard=1`: the DIMM guard is on the part). On the
clamshell: a rect seal across the lid's front edge and the papers (guide and safety as cards, warranty card); the lid
opens after them. Size: the module's length + 20 mm, its height + 20 mm, 25 mm thin.

### Foam carton: U.2 SSD, heatsinks and cards (`oem_u2`, `oem_heatsink`, `oem_card`)
A taped white corrugated slotted carton (`rig_products.rsc_box`: two long and two short top flaps, one tape strip
`A_TAPE_0..2`). Inside, a black PE foam "sandwich":
- **top foam** `A_INSERT_FOAM_1`: a pad with a die-cut pocket for the part's upper half, the papers on it;
- **bottom foam** `A_INSERT_FOAM_0`: the part's pocket (the part's posed bounds + the bag's margin), finger notches at
  its back edge, and one pocket per accessory in a row in front of the part.
- U.2: the drive flat, label up, in its silver bag. Heatsinks: base down (the base film is on the part), `bag=none`
  (their screws are captive). Cards: lying component side up, bracket to +x, in a silver bag; the low-profile bracket
  (`A_ITEM_ACC_0`, `id=<specs.lp_bracket>`, `frame=model`, `bag=clear`) lies flat in its own pocket; HBAs add a
  SFF-8654 cable coil (`A_ITEM_CORD_0`, `kind=sff8654`), the Verdia T100 its auxiliary 12V-2x6 power cable
  (`kind=12v2x6`).
Size: the pockets + 12 mm of foam around them, the foams' height + 6 mm for the papers.

### PSU: CRPS module (`oem_psu`)
A taped white slotted carton; the module lies flat (its own frame = the box axes) in its pink anti-static bag between
two white EPS end caps (`rig_products.eps_cap`, `A_INSERT_FOAM_0/1`, `with=A_ITEM_PART_0`: they come out with the
module and are pulled off along -x/+x); the papers lie in a pile across the module and the caps. No power cord: CRPS
modules ship without one.

### Board: server motherboard (`oem_board`)
A taped brown (kraft) slotted carton with brown tape. The board lies component side up, rear I/O to the back, in its
silver anti-static bag on a black PE foam pad (`A_INSERT_FOAM_0`) on a corrugated tray (`A_INSERT_CARD_0`, a deck on
folded legs with two finger holes). Under the tray, the accessory compartment: the I/O shield (`A_ITEM_ACC_0`,
`id=<specs.io_shield>`, `frame=model`, in a clear bag), an M.2 screw bag (`A_ITEM_HW_0`), the quick-start poster
folded on the manual, and the warranty card.

## Every box
| Box | Kind | Size (m) | Triangles | Opening sequence (by `order`) |
|---|---|---|---|---|
| `box_cpu_epoch_9124` | `oem_cpu` | 0.12 × 0.03 × 0.13 | 3562 | Server CPU: 2 seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> 2 papers on the clamshell, top first (3..4) -> PE foam pad A_INSERT_FOAM_0 lifted out with the clamshell (5) -> clear clamshell lid A_CLAMLID_0 (6) -> CPU in its carrier, bag=none (7) -> clamshell base A_INSERT_CLAM_0 (8). |
| `box_cpu_epoch_9354` | `oem_cpu` | 0.12 × 0.03 × 0.13 | 3562 | Server CPU: 2 seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> 2 papers on the clamshell, top first (3..4) -> PE foam pad A_INSERT_FOAM_0 lifted out with the clamshell (5) -> clear clamshell lid A_CLAMLID_0 (6) -> CPU in its carrier, bag=none (7) -> clamshell base A_INSERT_CLAM_0 (8). |
| `box_cpu_epoch_9654` | `oem_cpu` | 0.12 × 0.03 × 0.13 | 3562 | Server CPU: 2 seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> 2 papers on the clamshell, top first (3..4) -> PE foam pad A_INSERT_FOAM_0 lifted out with the clamshell (5) -> clear clamshell lid A_CLAMLID_0 (6) -> CPU in its carrier, bag=none (7) -> clamshell base A_INSERT_CLAM_0 (8). |
| `box_cpu_tiron_plat_8480` | `oem_cpu` | 0.11 × 0.03 × 0.16 | 3562 | Server CPU: 2 seals A_SEAL_0/1 (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> 2 papers on the clamshell, top first (3..4) -> PE foam pad A_INSERT_FOAM_0 lifted out with the clamshell (5) -> clear clamshell lid A_CLAMLID_0 (6) -> CPU in its carrier, bag=none (7) -> clamshell base A_INSERT_CLAM_0 (8). |
| `box_ram_kingsland_rdimm5_32` | `oem_rdimm` | 0.16 × 0.025 × 0.06 | 2810 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |
| `box_ram_sorin_rdimm5_64` | `oem_rdimm` | 0.16 × 0.025 × 0.06 | 2810 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |
| `box_ram_crux_rdimm5_128` | `oem_rdimm` | 0.16 × 0.025 × 0.065 | 2810 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |
| `box_ram_kingsland_rdimm4_32` | `oem_rdimm` | 0.16 × 0.025 × 0.06 | 2810 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |
| `box_ssd_sorin_pm9a3_3840` | `oem_u2` | 0.14 × 0.055 × 0.11 | 572 | OEM foam carton (oem_u2): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers on the top foam, top first (3..4) -> top foam A_INSERT_FOAM_1 (5) -> U.2 SSD in its bag (bag=antistatic_silver) in their pockets (6) -> bottom foam A_INSERT_FOAM_0 (7). |
| `box_ssd_sorin_pm9a3_7680` | `oem_u2` | 0.14 × 0.055 × 0.11 | 572 | OEM foam carton (oem_u2): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers on the top foam, top first (3..4) -> top foam A_INSERT_FOAM_1 (5) -> U.2 SSD in its bag (bag=antistatic_silver) in their pockets (6) -> bottom foam A_INSERT_FOAM_0 (7). |
| `box_cooler_srv_epoch_1u` | `oem_heatsink` | 0.13 × 0.075 × 0.155 | 572 | OEM foam carton (oem_heatsink): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> heatsink in its bag (bag=none) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_cooler_srv_platinum_2u` | `oem_heatsink` | 0.12 × 0.115 × 0.145 | 552 | OEM foam carton (oem_heatsink): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> heatsink in its bag (bag=none) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_psu_strata_crps_800` | `oem_psu` | 0.265 × 0.065 × 0.11 | 868 | CRPS PSU: tape strip 0 A_TAPE_0..2 (0) -> long flaps (1) -> short flaps (2) -> 3 papers in a pile, top first (3..5) -> the module in its pink bag, lifted out WITH its two EPS end caps (6) -> caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| `box_psu_strata_crps_1600` | `oem_psu` | 0.265 × 0.065 × 0.11 | 868 | CRPS PSU: tape strip 0 A_TAPE_0..2 (0) -> long flaps (1) -> short flaps (2) -> 3 papers in a pile, top first (3..5) -> the module in its pink bag, lifted out WITH its two EPS end caps (6) -> caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| `box_nic_linkwave_350t2` | `oem_card` | not built | | |
| `box_nic_linkwave_710da2` | `oem_card` | not built | | |
| `box_nic_melnet_strand6_25g` | `oem_card` | not built | | |
| `box_nic_melnet_strand6_100g` | `oem_card` | not built | | |
| `box_hba_broadline_9500_16i` | `oem_card` | not built | | |
| `box_hba_broadline_9560_16i` | `oem_card` | not built | | |
| `box_gpu_verdia_t100` | `oem_card` | not built | | |
| `box_gpu_voltra_mi210` | `oem_card` | not built | | |
| `box_mb_strata_spv` | `oem_board` | not built | | |
| `box_mb_strata_l46` | `oem_board` | not built | | |

## Deviations
- The CPU's papers lie on the clamshell lid under the tuck lid (the consumer CPU box stands them behind its tray):
  the OEM box is flat, there is no room behind the clamshell.
- HBA and accelerator cables use new `A_ITEM_CORD_0` kinds: `kind=sff8654` (an SFF-8654 x8 cable) and
  `kind=12v2x6` (the T100's auxiliary power cable); the contract lists `c13|dp|sata`.

## Requests for the shared code
- `A_ITEM_CORD` `kind=`: add `sff8654` and `12v2x6` to the documented kinds (`docs/PACKAGING.md` §2.2) and the
  game's cord look-up.

## Rebuild
From the repo root (Blender 4.x/5.x, or `bpy` with `run_bpy.py`):
```
blender -b --factory-startup -P Tools/Blender/build_boxes.py -- kind:oem_cpu kind:oem_rdimm kind:oem_u2 kind:oem_heatsink kind:oem_psu kind:oem_card kind:oem_board
```
(`--noshots` reuses the cached product shots, `--nopreview` skips the previews.)

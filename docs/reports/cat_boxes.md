# Catalogue 19: retail and OEM boxes for the catalogue

Brief: `docs/tasks/catalog/19-boxes.md`. Every catalogue part (`docs/catalog/*.json`) gets a box rig `box_<id>`,
plus the data-centre gear from task 01 and a rebuilt `box_ac_12k`.

## Status
**91 of 132 catalogue boxes built.** Not built yet: mb_aegis_x870e_vanguard, mb_mako_b650_harpoon, mb_kestrel_b650_glide, mb_aegis_z790_keystone, mb_mako_z790_riptide, mb_kestrel_z790_talon, mb_ridge_b760_d4, ram_gstride_ddr5_32_lp, ram_kingsland_ddr5_64, ram_kingsland_ddr5_32_white_rgb, ram_crux_ddr5_96, ram_crux_ddr5_16, ram_teamforge_ddr5_32_white_rgb, ram_volt_ddr5_64_rgb, ram_corvex_ddr4_16_lp, ram_corvex_ddr4_32_rgb, ram_gstride_ddr4_16_red, ram_kingsland_ddr4_32, ram_crux_ddr4_64, ram_teamforge_ddr4_32_red, ssd_crux_mx500_2tb, ssd_kingsland_a400_480, psu_seastar_px1000_white, psu_corvex_rm850x_white, psu_hush_pp12m_750, psu_hush_dp13_1200, psu_mako_a850g, psu_aegis_1200p, psu_corvex_ax1600i, cooler_arctiq_34_black, cooler_arctiq_34_white, cooler_glacier_ak400_white, cooler_glacier_ak620_black, cooler_noctis_d15_black, cooler_frostpeak_120_rgb, case_phanta_g360a, case_nexa_h5, case_facet_fjord, case_hush_500dx, case_facet_fizzair, case_brickhouse_beige98.

The work was split by rig module, each built and checked box by box (all four previews looked at):
- the consumer parts of the existing box kinds (`rig_products.py`): CPUs, GPUs, motherboards, memory, NVMe and SATA
  SSDs, ATX PSUs, air coolers and cases;
- the server and OEM parts (`rig_oem.py`), the rack gear with the task-01 gear, both racks and the AC (`rig_rack.py`),
  and the new consumer kinds: AIO, 3.5" HDD, fan packs, SFX PSU (`rig_new.py`), each by a helper session on its own
  branch, merged here; their sections follow below.

Besides the catalogue: the task-01 gear (server_1u, server_2u, switch_24, patch_panel_24, ups_2u, ups_tower, pdu_0u,
pdu_1u), rack_12u_open, rack_42u and the rebuilt box_ac_12k (hand-written items in `rig_rack.py`).

## How the catalogue path works
- **`Tools/Blender/box_catalog.py`** (new) reads `docs/catalog/*.json` and turns every part into a box item, so no
  box is hand-written:
  - **kind** (which rig) from the part's contract: `cpu_arc5`/`cpu_tiron5` → `cpu`, `gpu` → `gpu`, `mb_ridge_*` → `mb`,
    `ram` → `ram`, `ssd_1tb` → `ssd_m2`, `ssd_sata_500` → `ssd_sata`, `psu` → `psu`, `cooler_tower` → `cooler_tower`
    (under 80 mm tall: `cooler_low`), `cooler_stock` → `cooler_stock`, `case` → `case`; the new kinds `aio`, `hdd`,
    `hdd_bulk`, `fan_pack`, `psu_sfx`; the server kinds `oem_cpu`, `oem_rdimm`, `oem_u2`, `oem_heatsink`, `oem_psu`,
    `oem_card`, `oem_board`, `oem_rack`.
  - **the printed art** in the brand's look (`BRANDS`, with product-line overrides in `LINES` and white boxes for
    `_white` parts): colours, logo face, and the words written from the part's own specs (product line, key specs,
    badges, the CPU numeral). The product shot is rendered from the part's own FBX, as before.
  - **the papers**: the part's `"docs"` list, one `A_ITEM_DOC_n` per entry, `doc=` the catalogue's name
    (guide, quick-start, manual, warranty, sticker, driver, safety).
  - **the bounds** measured from the part's FBX (its own frame, Unity axes) and the **box size** from them
    (`box_catalog.size`, 5 mm steps). Rigs can also ask for the bounds of a slab or region of the model (the fin stack
    of a tower cooler, the cable stub of a fixed-cable PSU, the fan plug) to cut their pockets.
- **`build_boxes.py`** loads the catalogue items next to the hand-written `ITEMS`, and finds each kind's builder in the
  rig modules `rig_products`, `rig_oem`, `rig_rack`, `rig_new` (`RIG_MODULES`). A module may add hand-written items,
  adjust the catalogue items of its kinds, bring its own art (`ART`), size (`SIZE`) and previews. New print style
  `oem`: plain white or kraft board with a printed product label (brand sticker, name, P/N, bar code, S/N, QTY, ESD
  mark) on the front and one end, the brand on every side and handling marks on big cartons.
- **`rig_products.py`**: the existing builders take a catalogue item too. With one (`ctx.docs` set) they lay out the
  part's papers (`paper_list`, `pile`, `floor_papers`: side by side when they fit, else a pile whose top paper comes
  out first, each one `under` the one above), size their pockets, trays and caps from the measured part, and pick the
  variant from the part's facts:
  - GPU: the box follows the card's length, thickness and height; a pile of papers lifts the foam.
  - MB: the board's own I/O shield (`specs.io_shield`) as `A_ITEM_ACC_0` unless it is pre-attached; the
    quick-start poster lies on the manual.
  - RAM: the box depth follows the stick height; the papers lie in a pile on the blister lid, which opens after them.
  - SSD M.2: heatsink drives sit in a deeper blister (and a taller box).
  - PSU: the body length from `specs.depth_mm`; fully modular → EPS saddle caps, fabric bag, cable pouch, cord and
    screws in the end compartment; fixed cables → pulp cups (cap 0 has a hole at the measured cable stub), clear bag;
    semi-modular → the pulp version with the modular-cable pouch over the cord (a 0.135 tall box).
  - Tower cooler: against the back wall, the top EPS pocket cut to the measured fin stack, the bottom one with a
    channel at the measured fan plug, the accessory box in front holding the papers.
  - New `cooler_low` (the low-profile cooler): a printed tuck box, the cooler upright in a die-cut EPS tray, the
    accessory box beside it (mounting kit, paste syringe), the papers on top.
  - Stock cooler and case: the papers from the docs list (cards and stickers on the bags in the case's accessory box,
    the manual under them).
- **`rig_common.py`**: `shell()` now emits its faces in a canonical order (`canonical()`): bmesh's solidify ordered
  them differently on every run, so two exports of the same shell never compared SAME.

## Proof: the 24 existing rigs are unchanged
Old builders (`build_boxes.py`, `rig_products.py` as on `main`) and the new ones, both with this `rig_common.py`,
exported on Linux into a scratch project, compared with `Tools/Blender/extras_compare.py`:

```
COMPARE box_case_brickhouse: SAME (35 objects)
COMPARE box_case_breeze: SAME (35 objects)
COMPARE box_mb_ridge_b5: SAME (24 objects)
COMPARE box_mb_ridge_z4: SAME (24 objects)
COMPARE box_cpu_arc5: SAME (27 objects)
COMPARE box_cpu_arc7: SAME (27 objects)
COMPARE box_cpu_tiron5: SAME (27 objects)
COMPARE box_cooler_stock: SAME (19 objects)
COMPARE box_cooler_tower: SAME (36 objects)
COMPARE box_ram_ddr5_16: SAME (20 objects)
COMPARE box_ram_ddr4_8: SAME (20 objects)
COMPARE box_gpu_rx66: SAME (14 objects)
COMPARE box_gpu_rx88: SAME (14 objects)
COMPARE box_psu_450: SAME (31 objects)
COMPARE box_psu_750: SAME (32 objects)
COMPARE box_ssd_1tb: SAME (20 objects)
COMPARE box_ssd_sata_500: SAME (17 objects)
COMPARE box_usb_installer: SAME (10 objects)
COMPARE box_cable_dp: SAME (11 objects)
COMPARE box_fan_splitter: SAME (11 objects)
COMPARE box_cpu_arc9: SAME (27 objects)
COMPARE box_gpu_rx77: SAME (14 objects)
COMPARE box_mb_ridge_x5: SAME (24 objects)
COMPARE box_case_aero: SAME (35 objects)
```

Without the canonical shells, the untouched scripts themselves differ from run to run in the polygon order of every
shell mesh (clamshells, blisters, pulp caps, the SATA tray), with identical vertices; an order-independent compare
(every polygon as its vertex positions and UVs) showed those meshes identical too. The re-exports are not committed.

## Consumer boxes of the existing kinds
Opening sequence: the step `order` of each piece, from the rig's notes. Previews: `Logs/ModelPreviews/box_<id>_0..1`
(closed), `_2` (opened, the part in place), `_3` (exploded).

### CPUs
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_cpu_arc3_8300g | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_arc5_9600x | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_arc7_9700x | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_arc7_9800x3d | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_arc9_9950x3d | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_tiron_i3_14100 | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_tiron_i5_14600k | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_tiron_i7_14700 | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_tiron_i7_14700k | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |
| box_cpu_tiron_i9_14900k | 0.11 x 0.07 x 0.11 | 3612 | 13 | CPU: seals (0) -> tuck lid A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> tray A_INSERT_CARD_0 and the 3 papers behind it (3) -> clamshell lid A_CLAMLID_0 (4, on the tray once it is out) -> CPU (5) -> clamshell base (6). |

### Graphics cards
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_gpu_verdia_5060_zenith | 0.285 x 0.08 x 0.165 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_5060ti_aegis_white | 0.295 x 0.09 x 0.175 | 2158 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_5070_mako | 0.35 x 0.09 x 0.165 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_5070ti_kestrel_white | 0.37 x 0.09 x 0.175 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_5080_aegis | 0.41 x 0.11 x 0.2 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_5090_ref | 0.37 x 0.08 x 0.19 | 2158 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_5090_mako | 0.425 x 0.12 x 0.2 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_4060_kestrel_lp | 0.245 x 0.08 x 0.155 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_voltra_7600_zenith | 0.305 x 0.08 x 0.17 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_voltra_9060xt_zenith_white | 0.31 x 0.085 x 0.17 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_voltra_9070xt_zenith | 0.385 x 0.1 x 0.18 | 2158 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_voltra_7900xtx_ref | 0.35 x 0.09 x 0.175 | 2158 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_tiron_b580_ref | 0.335 x 0.085 x 0.165 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |

### Motherboards
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_mb_aegis_b650_bulwark | 0.32 x 0.07 x 0.27 | 502 | 14 | MB: side seals (0) -> hinged lid A_LID_0 (1) -> board in its bag (2, on the pad) -> foam pad (3) -> tray (4) -> compartment: I/O shield A_ITEM_ACC_0, SATA cables A_ITEM_CORD_0, M.2 screw bag A_ITEM_HW_0, poster, warranty, sticker (5) -> manual under the poster (6). |
| box_mb_aegis_x870e_vanguard | | | | **not built yet** |
| box_mb_mako_b650_harpoon | | | | **not built yet** |
| box_mb_kestrel_b650_glide | | | | **not built yet** |
| box_mb_aegis_z790_keystone | | | | **not built yet** |
| box_mb_mako_z790_riptide | | | | **not built yet** |
| box_mb_kestrel_z790_talon | | | | **not built yet** |
| box_mb_ridge_b760_d4 | | | | **not built yet** |

### Memory
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_ram_corvex_ddr5_32_black | 0.16 x 0.03 x 0.12 | 4350 | 11 | RAM: end tuck flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> blister tray A_INSERT_BLISTER_0 slides out +x (3) -> on it the blister seal A_SEAL_0 and 2 papers in a pile on the lid (4..5) -> blister lid A_CLAMLID_0 (6) -> sticks A_ITEM_PART_0/1 (7, guard=1). |
| box_ram_corvex_ddr5_32_white_rgb | 0.16 x 0.03 x 0.12 | 4350 | 11 | RAM: end tuck flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> blister tray A_INSERT_BLISTER_0 slides out +x (3) -> on it the blister seal A_SEAL_0 and 2 papers in a pile on the lid (4..5) -> blister lid A_CLAMLID_0 (6) -> sticks A_ITEM_PART_0/1 (7, guard=1). |
| box_ram_gstride_ddr5_48_rgb | 0.16 x 0.03 x 0.12 | 4350 | 11 | RAM: end tuck flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> blister tray A_INSERT_BLISTER_0 slides out +x (3) -> on it the blister seal A_SEAL_0 and 2 papers in a pile on the lid (4..5) -> blister lid A_CLAMLID_0 (6) -> sticks A_ITEM_PART_0/1 (7, guard=1). |
| box_ram_gstride_ddr5_32_lp | | | | **not built yet** |
| box_ram_kingsland_ddr5_64 | | | | **not built yet** |
| box_ram_kingsland_ddr5_32_white_rgb | | | | **not built yet** |
| box_ram_crux_ddr5_96 | | | | **not built yet** |
| box_ram_crux_ddr5_16 | | | | **not built yet** |
| box_ram_teamforge_ddr5_32_white_rgb | | | | **not built yet** |
| box_ram_volt_ddr5_64_rgb | | | | **not built yet** |
| box_ram_corvex_ddr4_16_lp | | | | **not built yet** |
| box_ram_corvex_ddr4_32_rgb | | | | **not built yet** |
| box_ram_gstride_ddr4_16_red | | | | **not built yet** |
| box_ram_kingsland_ddr4_32 | | | | **not built yet** |
| box_ram_crux_ddr4_64 | | | | **not built yet** |
| box_ram_teamforge_ddr4_32_red | | | | **not built yet** |
| box_ram_kingsland_rdimm5_32 | 0.16 x 0.025 x 0.06 | 2810 | 12 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |
| box_ram_sorin_rdimm5_64 | 0.16 x 0.025 x 0.06 | 2810 | 12 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |
| box_ram_crux_rdimm5_128 | 0.16 x 0.025 x 0.065 | 2810 | 12 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |
| box_ram_kingsland_rdimm4_32 | 0.16 x 0.025 x 0.06 | 2810 | 12 | RDIMM: seal A_SEAL_0 over the end flap (0) -> end flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> clamshell A_INSERT_BLISTER_0 slides out +x (3) -> on it: the clamshell seal A_SEAL_1 and the 3 papers, top first (4..6) -> clamshell lid A_CLAMLID_0 (7) -> module in its pink bag, guard=1 (8). |

### Storage
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_ssd_sorin_990pro_1tb | 0.11 x 0.025 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_sorin_990pro_2tb_hs | 0.11 x 0.025 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_sorin_980_500 | 0.11 x 0.025 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_westline_sn850x_2tb | 0.11 x 0.025 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_westline_sn850x_1tb_hs | 0.11 x 0.03 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_westline_sn580_1tb | 0.11 x 0.025 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_crux_p3plus_2tb | 0.11 x 0.025 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_crux_t705_2tb_hs | 0.11 x 0.04 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_sorin_870_1tb | 0.14 x 0.03 x 0.1 | 2868 | 9 | SSD SATA: seal (0) -> end flap (1) -> dust flaps (2) -> black tray A_INSERT_BLISTER_0 slides out +x (3) -> installation card lying on it (4) -> drive in its clear bag (5). |
| box_ssd_crux_mx500_2tb | | | | **not built yet** |
| box_ssd_kingsland_a400_480 | | | | **not built yet** |

### Power supplies
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_psu_ampere_550_bronze | 0.21 x 0.12 x 0.18 | 3138 | 16 | PSU (fixed cables): tape strip 0 (0) -> long flaps (1) -> short flaps (2) -> 3 papers in a pile, booklet at the bottom (3..5) -> power cord and screw bag on the PSU (6) -> PSU in its clear bag, lifted out WITH its pulp caps (7) -> caps pulled off along -x/+x (8). |
| box_psu_corvex_cx650m | 0.21 x 0.135 x 0.18 | 3138 | 17 | PSU (semi-modular): tape strip 0 (0) -> long flaps (1) -> short flaps (2) -> 3 papers in a pile, booklet at the bottom (3..5) -> cable pouch (6) -> power cord and screw bag on the PSU (7) -> PSU in its clear bag, lifted out WITH its pulp caps (8) -> caps pulled off along -x/+x (9). |
| box_psu_seastar_gx850 | 0.21 x 0.12 x 0.18 | 652 | 17 | PSU (fully modular): tape strip 0 (0) -> long flaps (1) -> short flaps (2) -> 3 papers in a pile, booklet at the bottom (3..5) with the power cord + screw bag standing in the +x compartment (3) -> cable pouch (6) -> PSU in its fabric bag, lifted out WITH its EPS caps (7) -> caps pulled off along -x/+x (8). |
| box_psu_seastar_px1000_white | | | | **not built yet** |
| box_psu_corvex_rm850x_white | | | | **not built yet** |
| box_psu_hush_pp12m_750 | | | | **not built yet** |
| box_psu_hush_dp13_1200 | | | | **not built yet** |
| box_psu_mako_a850g | | | | **not built yet** |
| box_psu_aegis_1200p | | | | **not built yet** |
| box_psu_corvex_ax1600i | | | | **not built yet** |

### Coolers
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_cooler_arctiq_34_black | | | | **not built yet** |
| box_cooler_arctiq_34_white | | | | **not built yet** |
| box_cooler_glacier_ak400_white | | | | **not built yet** |
| box_cooler_glacier_ak620_black | | | | **not built yet** |
| box_cooler_noctis_d15 | 0.185 x 0.215 x 0.21 | 1126 | 17 | Tower cooler: tape (0) -> long flaps (1) -> short flaps (2) -> top EPS A_INSERT_FOAM_0 (3) -> cooler A_ITEM_PART_0 and the accessory box A_INSERT_ACCBOX_0 standing in front of it (4) -> bottom EPS A_INSERT_FOAM_1 and the accessory box's tuck flap A_FLAP_4 (5) -> mounting kit A_ITEM_HW_0, paste syringe A_ITEM_HW_1 (kind=syringe, a look mesh on its anchor), manual A_ITEM_DOC_0 (6). |
| box_cooler_noctis_d15_black | | | | **not built yet** |
| box_cooler_frostpeak_120_rgb | | | | **not built yet** |
| box_cooler_noctis_l9 | 0.195 x 0.08 x 0.125 | 988 | 12 | Low-profile cooler: tuck lid A_FLAP_0 (1) -> dust flaps (2) -> 2 papers in a pile on top (3..4) -> cooler A_ITEM_PART_0 and the accessory box A_INSERT_ACCBOX_0 (5) -> EPS tray A_INSERT_FOAM_0 and the accessory box flap A_FLAP_3 (6) -> mounting kit A_ITEM_HW_0, paste A_ITEM_HW_1 (7). |
| box_cooler_tiron_stock | 0.12 x 0.09 x 0.15 | 4978 | 9 | Stock cooler: tuck lid A_FLAP_0 (1) -> dust flaps (2) -> clear clamshell A_INSERT_CLAM_0 lifted out (3) -> clamshell lid A_CLAMLID_0 and the leaflet under the clamshell (4) -> cooler (5). Box depth 0.15 (was 0.12): the model's fan plug sits 30 mm past the shroud, so the clamshell has a pocket for it behind the cooler. |

### Cases
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_case_lumin_216 | 0.52 x 0.56 x 0.3 | 1322 | 19 | Case: printed tape strip 0 (0) -> long flaps (1) -> short flaps (2) -> the case in its clear bag, lifted out by the foam (3) -> front/rear EPS caps A_INSERT_FOAM_0/1, with=A_ITEM_PART_0, pulled off along -x/+x (4). Accessory box A_INSERT_ACCBOX_0@A_ITEM_PART_0 sits INSIDE the case on the PSU shroud (case-frame pose relative to A_ITEM_PART_0), inside=A_PANEL_SIDE_0: take it out of the side opening (+z) once the glass panel is off (5) -> its tuck flap A_FLAP_4 (6) -> standoff bag A_ITEM_ACC_0 (id=standoff_bag, frame=flat), screws A_ITEM_HW_0, cable ties A_ITEM_HW_1 (6) -> manual A_ITEM_DOC_0 (7). |
| box_case_phanta_g360a | | | | **not built yet** |
| box_case_nexa_h5 | | | | **not built yet** |
| box_case_facet_fjord | | | | **not built yet** |
| box_case_hush_500dx | | | | **not built yet** |
| box_case_facet_fizzair | | | | **not built yet** |
| box_case_brickhouse_beige98 | | | | **not built yet** |

## Server and OEM part boxes (`rig_oem.py`)
Brief: `docs/tasks/catalog/19-boxes.md` ("server parts"). The coordinator folds this into `docs/reports/cat_boxes.md`
and writes `box` / `box_size` into the catalogue JSON (not done here).

### Status
**24 of 24 boxes built.** Done: cpu_epoch_9124, cpu_epoch_9354, cpu_epoch_9654, cpu_tiron_plat_8480, ram_kingsland_rdimm5_32, ram_sorin_rdimm5_64, ram_crux_rdimm5_128, ram_kingsland_rdimm4_32, ssd_sorin_pm9a3_3840, ssd_sorin_pm9a3_7680, cooler_srv_epoch_1u, cooler_srv_platinum_2u, psu_strata_crps_800, psu_strata_crps_1600, nic_linkwave_350t2, nic_linkwave_710da2, nic_melnet_strand6_25g, nic_melnet_strand6_100g, hba_broadline_9500_16i, hba_broadline_9560_16i, gpu_verdia_t100, gpu_voltra_mi210, mb_strata_spv, mb_strata_l46. Not built yet: none.

### What was made
- **`Tools/Blender/rig_oem.py`** (new rig module, listed in `build_boxes.RIG_MODULES`): the builders of the kinds
  `oem_cpu`, `oem_rdimm`, `oem_u2`, `oem_heatsink`, `oem_psu`, `oem_card` and `oem_board`, their `SIZE` (every box sized
  from the part's measured bounds, 5 mm steps), their `ART` and the `item()` hook.
- Per box: `Assets/Resources/Models/box_<id>.fbx`, `Textures/box_<id>.png` (the OEM print atlas),
  `Textures/box_<id>_in.png` (the inner print; the OEM rigs only use its swatches), previews
  `Logs/ModelPreviews/box_<id>_0..3.png` (closed front, closed back, opened with the contents in place, exploded) and
  `box_<id>_report.txt` (meshes and anchors).

### The print (`item()` and `ART`)
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

### The rig designs (one per size class, scaled to the part)
All rigs: origin at the bottom centre, +z the front, y up, closed pose, `A_HIT_0` = the outer size. Every paper of
the part's `docs` list is one `A_ITEM_DOC_n` (`rig_products.paper_list`, in a pile whose top paper comes out first,
each one `under` the one above it). The part's own caps, guards and films stay on the part (its `unbox` entry).

#### Small: server CPU (`oem_cpu`)
A white tuck-top carton (`rig_products.tuck_walls`, `tuck_lid_top`, `dust_flaps`, thumb notch in the front wall), two
round clear seals over the lid's front edge. Inside, a black PE foam pad with a die-cut window; the clamshell tray
(`rig_products.clamshell`: black moulded base with a ledge and a pocket, a **clear** hinged lid so the carrier shows)
sits in the window, parented to the pad, so the pad lifts out with the clamshell. The CPU lies pads down on the
ledge, in its carrier (`A_CARRIER_0` is part of the CPU model; the Arc Epoch carrier is orange, the Tiron Platinum one
black), its contact cover cap on the pads (on the part), `bag=none`. The papers lie on the clamshell lid.
Size: the clamshell flange (the part's footprint + 26 mm) + 10 mm, 30 mm tall.

#### Small: RDIMM (`oem_rdimm`)
A white end-tuck carton (`rig_products.end_tuck_box`) with a round seal over the end flap's top edge. A clear
clamshell (`rig_products.blister`, one cavity) slides out along +x; the module lies in it label side up, gold fingers
to the front, in its pink anti-static bag (`bag=antistatic_pink`, `guard=1`: the DIMM guard is on the part). On the
clamshell: a rect seal across the lid's front edge and the papers (guide and safety as cards, warranty card); the lid
opens after them. Size: the module's length + 20 mm, its height + 20 mm, 25 mm thin.

#### Foam carton: U.2 SSD, heatsinks and cards (`oem_u2`, `oem_heatsink`, `oem_card`)
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

#### PSU: CRPS module (`oem_psu`)
A taped white slotted carton; the module lies flat (its own frame = the box axes) in its pink anti-static bag between
two white EPS end caps (`rig_products.eps_cap`, `A_INSERT_FOAM_0/1`, `with=A_ITEM_PART_0`: they come out with the
module and are pulled off along -x/+x); the papers lie in a pile across the module and the caps. No power cord: CRPS
modules ship without one.

#### Board: server motherboard (`oem_board`)
A taped brown (kraft) slotted carton with brown tape. The board lies component side up, rear I/O to the back, in its
silver anti-static bag on a black PE foam pad (`A_INSERT_FOAM_0`) on a corrugated tray (`A_INSERT_CARD_0`, a deck on
folded legs with two finger holes). Under the tray, the accessory compartment: the I/O shield (`A_ITEM_ACC_0`,
`id=<specs.io_shield>`, `frame=model`, in a clear bag), an M.2 screw bag (`A_ITEM_HW_0`), the quick-start poster
folded on the manual, and the warranty card.

### Every box
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
| `box_nic_linkwave_350t2` | `oem_card` | 0.18 × 0.06 × 0.19 | 712 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> network card in its bag (bag=antistatic_silver) and A_ITEM_ACC_0 (bracket) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_nic_linkwave_710da2` | `oem_card` | 0.22 × 0.06 × 0.19 | 788 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> network card in its bag (bag=antistatic_silver) and A_ITEM_ACC_0 (bracket) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_nic_melnet_strand6_25g` | `oem_card` | 0.22 × 0.06 × 0.19 | 788 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> network card in its bag (bag=antistatic_silver) and A_ITEM_ACC_0 (bracket) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_nic_melnet_strand6_100g` | `oem_card` | 0.22 × 0.06 × 0.19 | 788 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> network card in its bag (bag=antistatic_silver) and A_ITEM_ACC_0 (bracket) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_hba_broadline_9500_16i` | `oem_card` | 0.22 × 0.06 × 0.25 | 876 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> storage controller in its bag (bag=antistatic_silver) and A_ITEM_ACC_0 (bracket), A_ITEM_CORD_0 (cord) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_hba_broadline_9560_16i` | `oem_card` | 0.28 × 0.06 × 0.25 | 872 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers on the top foam, top first (3..6) -> top foam A_INSERT_FOAM_1 (7) -> storage controller in its bag (bag=antistatic_silver) and A_ITEM_ACC_0 (bracket), A_ITEM_CORD_0 (cord) in their pockets (8) -> bottom foam A_INSERT_FOAM_0 (9). |
| `box_gpu_verdia_t100` | `oem_card` | 0.32 × 0.085 × 0.245 | 720 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> accelerator card in its bag (bag=antistatic_silver) and A_ITEM_CORD_0 (cord) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_gpu_voltra_mi210` | `oem_card` | 0.32 × 0.085 × 0.165 | 600 | OEM foam carton (oem_card): tape strip 0 A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers on the top foam, top first (3..5) -> top foam A_INSERT_FOAM_1 (6) -> accelerator card in its bag (bag=antistatic_silver) in their pockets (7) -> bottom foam A_INSERT_FOAM_0 (8). |
| `box_mb_strata_spv` | `oem_board` | 0.36 × 0.065 × 0.325 | 468 | Server board: tape strip 0 A_TAPE_0..2 (0) -> long flaps (1) -> short flaps (2) -> board in its silver bag (3, on the pad) -> PE foam pad A_INSERT_FOAM_0 (4) -> cardboard tray A_INSERT_CARD_0 (5) -> compartment: I/O shield A_ITEM_ACC_0, screw bag A_ITEM_HW_0, quick-start poster and warranty card (6) -> manual under the poster (7). |
| `box_mb_strata_l46` | `oem_board` | 0.36 × 0.065 × 0.325 | 468 | Server board: tape strip 0 A_TAPE_0..2 (0) -> long flaps (1) -> short flaps (2) -> board in its silver bag (3, on the pad) -> PE foam pad A_INSERT_FOAM_0 (4) -> cardboard tray A_INSERT_CARD_0 (5) -> compartment: I/O shield A_ITEM_ACC_0, screw bag A_ITEM_HW_0, quick-start poster and warranty card (6) -> manual under the poster (7). |

### Deviations
- The CPU's papers lie on the clamshell lid under the tuck lid (the consumer CPU box stands them behind its tray):
  the OEM box is flat, there is no room behind the clamshell.
- HBA and accelerator cables use new `A_ITEM_CORD_0` kinds: `kind=sff8654` (an SFF-8654 x8 cable) and
  `kind=12v2x6` (the T100's auxiliary power cable); the contract lists `c13|dp|sata`.

- The U.2 and heatsink exploded previews (`_3`) were rendered before the foam-carton explode offsets were last
  tuned for the cards (the top foam now explodes up and back); their models are unchanged by it. A rebuild refreshes them.
- `rig.check()` prints no `RIG CHECK` line for any of the 24 boxes.

### Requests for the shared code
- `A_ITEM_CORD` `kind=`: add `sff8654` and `12v2x6` to the documented kinds (`docs/PACKAGING.md` §2.2) and the
  game's cord look-up.

### Rebuild
From the repo root (Blender 4.x/5.x, or `bpy` with `run_bpy.py`):
```
blender -b --factory-startup -P Tools/Blender/build_boxes.py -- kind:oem_cpu kind:oem_rdimm kind:oem_u2 kind:oem_heatsink kind:oem_psu kind:oem_card kind:oem_board
```
(`--noshots` reuses the cached product shots, `--nopreview` skips the previews.)

## Rack gear, the task-01 gear, the racks and the AC (`rig_rack.py`)
Module `Tools/Blender/rig_rack.py` (a `build_boxes.RIG_MODULES` entry), branch `claude/boxes-rack`.

### Status
**All 20 boxes are built**, each with four previews (`_0`/`_1` closed, `_2` opened, `_3` exploded) that I looked at. No box
printed a `RIG CHECK` line.
- Catalogue (`oem_rack`): srv_strata_sg840_4u, srv_strata_sr224_2u, srv_linkwave_ls4804x, srv_linkwave_ls1600x,
  srv_strata_shelf_1u, srv_strata_blank_1u, srv_strata_blank_2u, srv_strata_cma, srv_strata_kvm_1u.
- Task-01 gear (hand-written `ITEMS` in the module): server_1u, server_2u, switch_24, patch_panel_24, pdu_1u, ups_2u,
  ups_tower, pdu_0u, rack_12u_open, rack_42u, and ac_12k (it replaces the old 4-flap `box_ac_12k`).

Not done: nothing in this group. I did not touch the catalogue JSON (the coordinator writes `box`/`box_size`).

### Rebuild
```bash
~/bpyenv/bin/python ~/run_bpy.py Tools/Blender/build_boxes.py -- kind:oem_rack server_1u server_2u switch_24 \
  patch_panel_24 pdu_1u ups_2u ups_tower pdu_0u rack_12u_open rack_42u ac_12k
```
(`kind:oem_rack` also selects the hand-written items of that kind; add `--noshots` to reuse the product shots.)

### Boxes
Size is A_HIT_0 (x × y × z, m); the opening sequence gives each step's `order`, from the rig's notes.

| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_server_1u | 0.85 x 0.125 x 0.52 | 2340 | 21 | 1U carton (pe foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 2 x C13 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the device in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_server_2u | 0.88 x 0.175 x 0.525 | 3148 | 22 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 2 x C13 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the device in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws and bezel keys in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_srv_strata_sr224_2u | 0.865 x 0.175 x 0.525 | 2336 | 21 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 2 x C13 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the device in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_srv_strata_sg840_4u | 0.895 x 0.275 x 0.535 | 2340 | 21 | 4U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> rail-kit box A_INSERT_ACCBOX_0, 4 x C19 power cord A_ITEM_CORD_0 (7) -> its tuck flap A_FLAP_4, the server in its antistatic pink bag, lifted out WITH its end caps (8) -> rail screws in the box, end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9) -> slide rails A_ITEM_HW (kind=rail, look meshes) (10). |
| box_ups_2u | 0.6 x 0.16 x 0.525 | 928 | 19 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> C19 power cord A_ITEM_CORD_0, USB cable A_ITEM_CORD_1, hardware bag A_ITEM_HW_0 (7) -> the device in its clear bag, lifted out WITH its end caps (8) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x, the battery warning tag A_STICKER_0@A_ITEM_PART_0 on the bezel (blocks A_BEZEL_0: peel it, take the bezel off, connect the battery) (9). |
| box_ups_tower | 0.57 x 0.275 x 0.21 | 924 | 17 | 2U carton (eps foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> USB cable A_ITEM_CORD_0 (7) -> the device in its clear bag, lifted out WITH its end caps (8) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x, the battery warning tag A_STICKER_0@A_ITEM_PART_0 on the bezel (blocks A_BEZEL_0: peel it, take the bezel off, connect the battery) (9). |
| box_switch_24 | 0.555 x 0.1 x 0.29 | 908 | 18 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> C13 power cord A_ITEM_CORD_0, console cable A_ITEM_CORD_1, hardware bags A_ITEM_HW_0/A_ITEM_HW_1 (6) -> the device in its antistatic pink bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_linkwave_ls4804x | 0.555 x 0.1 x 0.32 | 908 | 18 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> C13 power cord A_ITEM_CORD_0, console cable A_ITEM_CORD_1, hardware bags A_ITEM_HW_0/A_ITEM_HW_1 (6) -> the device in its antistatic pink bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_linkwave_ls1600x | 0.555 x 0.1 x 0.34 | 908 | 16 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> 2 x C13 power cord A_ITEM_CORD_0, hardware bag A_ITEM_HW_0 (6) -> the device in its antistatic pink bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_strata_kvm_1u | 0.855 x 0.105 x 0.525 | 908 | 18 | 1U carton (pe foam end caps, x-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 4 papers in a pile, the first on top (3..6) -> C13 power cord A_ITEM_CORD_0, VGA + USB console cable A_ITEM_CORD_1, hardware bag A_ITEM_HW_0 (7) -> the device in its antistatic pink bag, lifted out WITH its end caps (8) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (9). |
| box_pdu_1u | 0.555 x 0.09 x 0.27 | 908 | 15 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> hardware bag A_ITEM_HW_0 (6) -> the device in its clear bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_srv_strata_shelf_1u | 0.555 x 0.09 x 0.44 | 908 | 14 | 1U carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the device in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_patch_panel_24 | 0.52 x 0.075 x 0.185 | 1076 | 15 | Panel carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bags A_ITEM_HW_0/A_ITEM_HW_1 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_srv_strata_blank_1u | 0.52 x 0.05 x 0.115 | 516 | 14 | Panel carton (pe foam end caps, up-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_srv_strata_blank_2u | 0.52 x 0.05 x 0.16 | 516 | 14 | Panel carton (pe foam end caps, up-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_srv_strata_cma | 0.485 x 0.07 x 0.215 | 916 | 14 | Panel carton (pe foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> hardware bag A_ITEM_HW_0 (5) -> the panel in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_pdu_0u | 1.94 x 0.125 x 0.08 | 908 | 15 | 1U carton (pe foam end caps, pdu-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 3 papers in a pile, the first on top (3..5) -> hardware bag A_ITEM_HW_0 (6) -> the device in its clear bag, lifted out WITH its end caps (7) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (8). |
| box_ac_12k | 0.78 x 0.535 x 0.7 | 1068 | 15 | AC carton (eps foam end caps, z-facing): tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers in a pile, the first on top (3..4) -> wall trim A_ITEM_KIT_0 (look piece), hardware bag A_ITEM_HW_0 (5) -> the AC unit in its clear bag, lifted out WITH its end caps (6) -> end caps A_INSERT_FOAM_0/1 pulled off along -x/+x (7). |
| box_rack_12u_open | 0.825 x 0.17 x 0.595 | 4136 | 22 | 12U open frame, flat-packed: tape A_TAPE_0..2 (0) -> long flaps A_FLAP_0/1 (1) -> short flaps A_FLAP_2/3 (2) -> 2 papers on the hardware bags (3..4) -> castor bag A_ITEM_KIT_0, cage nuts A_ITEM_HW_0 and screws A_ITEM_HW_1 (5) -> 4 posts A_ITEM_KIT_1..4, tie bar A_ITEM_KIT_5 and the top frame A_ITEM_KIT_6 (6) -> cardboard divider A_INSERT_CARD_0 (7) -> bottom frame A_ITEM_KIT_7 (8) -> assembly: the rack A_ITEM_PART_0 spawns standing in front of the carton (spawn=assembled), the KIT look pieces go (9). |
| box_rack_42u | 0.8 x 2.1664 x 1.2 | 1532 | 21 | 42U rack on a pallet: strapping bands A_STRAP_0..3 (cut) (0) -> stretch film in five sheets A_INSERT_WRAP_0..4 (front, +x, back, -x, top) (1) -> top cap A_INSERT_CARD_4, the tape A_TAPE_0 over the keys on the front door (2) -> corner posts A_INSERT_CARD_0..3, on the roof: 2 papers (3..4) and the cage-nut kit A_ITEM_HW_0, the door keys A_ITEM_HW_1 (kind=keys, for the front door lock) (3) -> the rack A_ITEM_PART_0 rolls off the pallet (4). |

### Rig designs
#### `build_carton` (kinds `oem_rack` and `ac`): one design per size class, scaled
A taped regular slotted carton (`rig_products.rsc_box`), printed with `build_boxes.compose_oem`: plain kraft or white
board, the brand on every side, the product label (brand sticker, name, P/N, bar code, S/N, QTY, ESD mark) on the front
and one end, and handling marks on the big ones. The AC uses `compose` in the carton style instead (see below).
- **The device** lies in it (`A_ITEM_PART_0`, the part's own frame) in its bag:
  - `antistatic_pink`: the servers, the switches and the KVM;
  - `clear`: the UPSs, the PDUs, the passive metalwork and the AC.
- **Two foam end caps** (`A_INSERT_FOAM_0/1`, `with=A_ITEM_PART_0`) hold its ends: the part comes out with them, then
  they pull off along −x/+x. Each cap is die-cut with a pocket for the part's measured section, two recesses on the wall
  side, and a finger notch on its inner face.
- **The top layer**, between the caps on top of the bag, is shelf-packed from the part's facts (`RIGCFG`):
  - the rail-kit box `A_INSERT_ACCBOX_0` with its tuck flap `A_FLAP_4`. It holds the slide rails, the rail screws and
    (server_2u) the bezel keys;
  - the cords `A_ITEM_CORD_n` (`kind=`, `n=` = how many are coiled together);
  - the hardware bags `A_ITEM_HW_n`;
  - look-only kit pieces `A_ITEM_KIT_n`.
- **The papers** lie in a pile on the first (largest) layer item, the top one first, one `A_ITEM_DOC` per entry of the
  part's `docs`.
- **Order:** tape (0) → long flaps (1) → short flaps (2) → papers (3..) → the layer items → the part with its caps →
  the caps.
- **Orientation:** the part's longest horizontal side runs along the box x (`ORIENT`), so the flaps meet across the
  short side as on a real carton:
  - deep devices (servers, UPSs, KVM) lie front to +x;
  - wide ones (switches, PDU, shelf, patch panel, CMA) lie front to +z;
  - the blanking panels lie face up;
  - the zero-U PDU lies along x with its outlets up.
- **Size classes** (`CLASSES`); the box size comes from the measured bounds plus the class margins, in 5 mm steps:

| Class | Board | Caps | Cap end / pocket | Used by |
|---|---|---|---|---|
| 1U | 4 mm, kraft or white | black PE | 30 / 40 mm | server_1u, KVM, switches, pdu_1u, pdu_0u, shelf |
| 2U | 5 mm kraft | white EPS | 35 / 45 mm | server_2u, sr224, ups_2u, ups_tower |
| 4U | 7 mm (double wall) kraft | white EPS | 45 / 55 mm | sg840 |
| panel | 3 mm white, clear tape | black PE | 15 / 20 mm, 30 mm side walls | patch panel, blanks, CMA |
| AC | 5 mm kraft, printed | white EPS | 35 / 40 mm, 25 mm side walls | ac_12k |

- **Servers** (server_1u, server_2u, sr224, sg840): a big brown carton with end foam, the anti-static bag, a rail-kit
  box and the quick-start sheet plus the rest of the part's papers. **The rails are look meshes on `A_ITEM_HW` anchors**
  (`kind=rail,side=l|r,len=0.62,look=1`), because there is no rail model. Each one shows the collapsed outer and inner
  members, the end brackets with pins, and the release tabs; the rail kit's label is `tex_box_<id>_kit`.
  - The KVM has its slides fixed on the model, so it brings rear brackets (HW) instead of a rail kit.
  - The sg840's four C19 cords are one coil, `n=4`.
- **UPSs** (ups_2u, ups_tower): `A_ITEM_PART_0` carries `battery=disconnected`. The battery warning tag is
  `A_STICKER_0@A_ITEM_PART_0`, a yellow printed tag with a tape strip stuck on the front bezel (the part's frame:
  ups_2u (−0.052, 0.0445, 0.0334), ups_tower (0, 0.095, 0.220)). Its meta is
  `shape=rect,peel=+y,kind=warning_tag,print=BATTERY DISCONNECTED,blocks=A_BEZEL_0`. It is reachable once the UPS is out
  of the box, and it blocks the bezel, so the order is: peel the tag → take off the bezel → connect the battery
  `A_BATTERY_0`. The game moves it with the part (it is parented to the part).
- **ac_12k** (exempt from the SAME proof): the old box was the generic size with a stand-in shot of a split-type unit.
  - The new art is the carton style (`compose`): the FrostLine brand and a flexo line drawing rendered from `ac_12k.fbx`
    (the through-the-wall unit), "THROUGH-THE-WALL AIR CONDITIONER", TW-12K, the specs and handling marks.
  - Inside: the EPS end caps, the unit in a clear bag (front +z), the wall trim (look piece `A_ITEM_KIT_0`,
    `member=wall_trim`), the hardware bag `A_ITEM_HW_0`, the manual and the warranty card.

#### `build_flatpack` (kind `rack_flatpack`): rack_12u_open
The open frame flat-packed in a long kraft carton, from the bottom:
- the bottom frame (with its castor plates);
- a cardboard divider `A_INSERT_CARD_0`;
- the top frame, with the four C-profile posts and the cable tie bar nested in its opening;
- on top: the castor bag, the cage-nut bag and the screw bag, with the papers on the bags.

**The mapping to the part:** the members are look pieces on `A_ITEM_KIT_n`, with `kit=rack_12u_open`,
`member=bottom_frame|top_frame|post|tie_bar|castors` and `look=1`, plus `lift`/`order`/`under` like any insert. The
assembled rack is `A_ITEM_PART_0`, standing in front of the carton (its own frame, on the floor), with meta
`kit=1,spawn=assembled` and `under=` every KIT anchor. So the game spawns the built rack there once every member is out
(the assembly step) and deletes the KIT look pieces. The opened preview hides the assembled rack; the exploded preview
shows it.

#### `build_pallet` (kind `rack_pallet`): rack_42u
- **The body** is a wooden EUR pallet (1200 × 800 × 144: 3 bottom boards, 9 blocks, 3 cross boards, 5 deck boards). It
  has its own atlas `tex_box_rack_42u`: the wood grain and knots, the IPPC/EPAL stamps on the front blocks, the corner
  post and top cap print, the product label and the key tag.
- **The rack** stands on the deck (`A_ITEM_PART_0`, `bag=none`).
- **Order:**
  - 0: the strapping bands `A_STRAP_0..3` (`kind=pp_band,cut=1`): two over the top and through the pallet's fork
    openings, two round the posts, each with a metal seal.
  - 1: the stretch film in five big sheets `A_INSERT_WRAP_0..4` (front, +x, back, −x, top;
    `kind=stretch_film,peel=+y,lift=<outward>`), each `under` the bands that cross it.
  - 2: the top cap `A_INSERT_CARD_4` (a corrugated tray upside down over the roof and the post tops), and the tape
    `A_TAPE_0@A_ITEM_PART_0` over the keys.
  - 3: the corner posts `A_INSERT_CARD_0..3` (printed cardboard L angles); the papers and the cage-nut kit lying on the
    roof under the cap (parented to the part); and the door keys `A_ITEM_HW_1@A_ITEM_PART_0` (`kind=keys,look=1`, two
    keys on a ring in a clear bag), taped to the front door by the handle.
  - 4: the rack rolls off the pallet.
- The closed views show the empty wrap, because the rack is spawned by the game, not part of the rig model.

### Deviations
- **New anchor kinds** beyond the contract table: `A_ITEM_KIT_n` (look-only loose contents with no PartDef model: the
  flat-pack members, the AC wall trim), `A_STRAP_n` (bands to cut) and `A_STICKER_0@A_ITEM_PART_0` (the UPS warning tag).
  `A_INSERT_WRAP` is used for the stretch film (the contract has it for bubble wrap).
- **Anchors that carry their own look mesh** (rails, keys, kit pieces) have `look=1`, so the game can keep the mesh
  rather than spawning a bag.
- **New cord kinds:** `c19`, `usb`, `console` and `kvm`, plus a second cord anchor `A_ITEM_CORD_1`. Cords carry `n=` for
  several cords coiled together.
- **ac_12k box size** grows from the old `BoxSize` 0.68 × 0.48 × 0.62 to **0.78 × 0.535 × 0.70**: the through-the-wall
  unit is 0.70 × 0.48 × 0.64, plus its caps. The wall trim is also part of the AC model's static mesh, so the box's trim
  is a look piece the game removes at install.
- The rack_12u and rack_42u items are hand-written (`kind` rack_flatpack/rack_pallet); their art does not use the
  product shot.

### Requests for the shared code
- The Unity contract (PACKAGING.md 2.2) should add: `A_ITEM_KIT_n`, `A_STRAP_n`, `A_STICKER_n` on a part
  (`blocks=`), `A_INSERT_WRAP` with `kind=stretch_film`, `look=1`, `A_ITEM_CORD_n` for n > 0, the cord kinds
  c19/usb/console/kvm with `n=`, `A_ITEM_PART_0` with `spawn=assembled,kit=1` and `battery=disconnected`.
- `rig_products.previews` could take a fill for the closed views and a list of anchors to hide in the opened view.
  `rig_rack.previews` copies it with those two additions.
- `rig_products.add_contents` could skip anchors with `look=1`. `rig_rack.add_contents` filters them out.
- The OEM print (`compose_oem`) prints the side faces' logo very small on long, low boxes. It reads at arm's length,
  but a size relative to the face height would read better.

## New consumer kinds: AIO, 3.5" HDD, fan packs, SFX PSU (`rig_new.py`)
Brief: `docs/tasks/catalog/19-boxes.md` (the new kinds: AIO, 3.5" HDD retail and bulk, fan packs, SFX PSU). Module
`Tools/Blender/rig_new.py` (plugged into `build_boxes.RIG_MODULES`), branch `claude/boxes-new`.

### Status
**All 15 boxes of this group are built** (`rig.check()` prints no `RIG CHECK` line for any of them).

| kind | ids | state |
|---|---|---|
| `hdd` | hdd_seacrest_2tb, hdd_westline_4tb, hdd_seacrest_8tb | done |
| `hdd_bulk` | hdd_seacrest_exos_20tb | done |
| `fan_pack` | fan_arctiq_p12_5pack, fan_noctis_a12x25, fan_noctis_a12x25_black, fan_lumin_sl120_white_3pack, fan_corvex_af120_rgb_3pack, fan_arctiq_p14, fan_hush_wing4_140 | done |
| `aio` | cooler_arctiq_lc240, cooler_corvex_h150i_white, cooler_glacier_ls720 | done |
| `psu_sfx` | psu_corvex_sf750 | done |

### Boxes

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

### Rig designs

#### `hdd`: 3.5" desktop drive, retail
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

#### `hdd_bulk`: enterprise 3.5" drive, bulk pack
- **Box:** a brown single-wall carton (`rsc_box`, 3 mm board, brown packing tape strip), printed in the plain OEM
  style on kraft (`style=oem`, `oem_base=kraft`): the brand in one ink, the white product label (P/N, bar code, S/N,
  QTY, ESD mark) on the front and one end.
- **Inserts:** two black PE foam end caps (`A_INSERT_FOAM_0/1`, `with=A_ITEM_PART_0`), each a block with a pocket for
  the drive's end and a finger slot on top; the drive floats in the middle of the box between them.
- **Contents:** the drive in a silver anti-static bag; the papers in a pile on the caps.

#### `psu_sfx`: SFX PSU
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

#### `fan_pack`: case fans, window box
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

#### `aio`: AIO liquid cooler
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

### Deviations
- **AIO fans:** the brief says "fans in a separate compartment". In the AIO models the fans are mounted on the
  radiator (one model, `A_RAD_FAN_k@A_RAD_0`), as the Arctiq unit really ships, so there are no separate fan items to
  box: the radiator lies with its fans in the pulp tray and the separate compartment holds the accessory box. If the
  cooler models ever split the fans off, add `A_ITEM_ACC_n` per fan in that compartment.
- **AIO bag:** none (`bag=none`): the code's bag is a box around the whole part's bounds, which would wrap pump, tubes
  and radiator together.
- **Fan box windows** hide part of the front print (the shared art does not know about the windows).

### Requests for the shared code
- `build_boxes.band_face`: with a wide logo (WESTLINE, ARCTIQ in their fonts) the logo runs into the product name on
  short faces (the HDD box front, the fan boxes' top): limit the logo to the space left of the name (or start the
  name after the logo's measured width).
- `build_boxes.compose`: an optional per-item list of window cut-outs (face, centre, radius) so the hero art can keep
  the logo and name clear of them (fan_pack).
- `rig_products.previews`: an option (e.g. `rig.contents_closed = True`) to place the contents before the closed
  shots; `rig_new.previews` copies the function to do this for the window boxes.

### Rebuild
```
<python> run_bpy.py Tools/Blender/build_boxes.py -- kind:hdd kind:hdd_bulk kind:fan_pack kind:aio kind:psu_sfx
```
(`blender -b --factory-startup -P Tools/Blender/build_boxes.py -- ...` on Windows; `--noshots` reuses the cached
product shots, `--nopreview` skips the previews.)

## For the game: additions to the packaging contract (PACKAGING.md 2.2)
Everything else follows the contract as it is. The new names, all of them in the rigs' anchor meta:
- **Papers:** `doc=` uses the catalogue's kinds; `quick-start` is new next to guide, manual, warranty, sticker, driver,
  safety. Every box has exactly one `A_ITEM_DOC_n` per entry of its part's `docs` list.
- **Cords:** new `kind=` values `c19`, `usb`, `console`, `kvm`, `sff8654`, `12v2x6`; a second cord `A_ITEM_CORD_1`;
  `n=` for several cords coiled together.
- **Look-only contents:** `A_ITEM_KIT_n` (flat-pack rack members, the AC's wall trim) and `look=1` on anchors that carry
  their own mesh (server rails `kind=rail`, rack keys `kind=keys`, the paste syringe `kind=syringe`): the game keeps the
  mesh instead of spawning an item or a bag.
- **Racks:** `A_STRAP_n` (strapping bands, `kind=pp_band,cut=1`), `A_INSERT_WRAP_n` with `kind=stretch_film`
  (the contract had WRAP for bubble wrap), `A_ITEM_PART_0` with `kit=1,spawn=assembled` (the flat-packed 12U rack is
  spawned built once its members are out).
- **UPS:** `battery=disconnected` on `A_ITEM_PART_0` and the warning tag `A_STICKER_0@A_ITEM_PART_0`
  (`kind=warning_tag,blocks=A_BEZEL_0`), riding on the part.
- **Box sizes:** every catalogue part's box size is in its catalogue entry (`box_size`), for `PartFactory.BoxSize`.
  `box_ac_12k` grows from 0.68 x 0.48 x 0.62 to 0.78 x 0.535 x 0.70 (the through-the-wall unit and its caps).

## Deviations
- **AIO fans** ship mounted on the radiator: the AIO models are one model with their fans on it, so the "separate
  compartment" holds the accessory box, not the fans (see the new-kinds section).
- The **window boxes** (fan packs) print the regular retail art; the window hides part of the front print.
- Tower coolers keep the existing rig's layout: the papers stand in the accessory box with the mounting kit.

## Rebuild
```
blender -b --factory-startup -P Tools/Blender/build_boxes.py -- --catalog          # every catalogue box
blender -b --factory-startup -P Tools/Blender/build_boxes.py -- cpus gpus           # by family
blender -b --factory-startup -P Tools/Blender/build_boxes.py -- kind:psu            # by box kind
blender -b --factory-startup -P Tools/Blender/build_boxes.py -- cpu_arc5_9600x      # one box
blender -b --factory-startup -P Tools/Blender/box_catalog.py -- --json             # writes box / box_size into the catalogue
```
Add `--noshots` to reuse the cached product shots, `--nopreview` to skip the previews.

## README line
`Tools/Blender/build_boxes.py -- --catalog`: the retail and OEM box rigs of every catalogue part (box_<id>), from docs/catalog/*.json (box_catalog.py; rigs in rig_products.py, rig_oem.py, rig_rack.py, rig_new.py).

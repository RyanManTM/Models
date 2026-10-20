# Catalogue 19: retail and OEM boxes for the catalogue

Brief: `docs/tasks/catalog/19-boxes.md`. Every catalogue part (`docs/catalog/*.json`) gets a box rig `box_<id>`,
plus the data-centre gear from task 01 and a rebuilt `box_ac_12k`.

## Status
**17 of 132 catalogue boxes built.** Not built yet: cpu_tiron_i3_14100, cpu_tiron_i5_14600k, cpu_tiron_i7_14700, cpu_tiron_i7_14700k, cpu_tiron_i9_14900k, cpu_epoch_9124, cpu_epoch_9354, cpu_epoch_9654, cpu_tiron_plat_8480, gpu_verdia_5060ti_aegis_white, gpu_verdia_5070_mako, gpu_verdia_5070ti_kestrel_white, gpu_verdia_5080_aegis, gpu_verdia_5090_ref, gpu_verdia_5090_mako, gpu_verdia_4060_kestrel_lp, gpu_voltra_7600_zenith, gpu_voltra_9060xt_zenith_white, gpu_voltra_9070xt_zenith, gpu_voltra_7900xtx_ref, gpu_tiron_b580_ref, gpu_verdia_t100, gpu_voltra_mi210, mb_aegis_x870e_vanguard, mb_mako_b650_harpoon, mb_kestrel_b650_glide, mb_aegis_z790_keystone, mb_mako_z790_riptide, mb_kestrel_z790_talon, mb_ridge_b760_d4, mb_strata_spv, mb_strata_l46, ram_corvex_ddr5_32_white_rgb, ram_gstride_ddr5_48_rgb, ram_gstride_ddr5_32_lp, ram_kingsland_ddr5_64, ram_kingsland_ddr5_32_white_rgb, ram_crux_ddr5_96, ram_crux_ddr5_16, ram_teamforge_ddr5_32_white_rgb, ram_volt_ddr5_64_rgb, ram_corvex_ddr4_16_lp, ram_corvex_ddr4_32_rgb, ram_gstride_ddr4_16_red, ram_kingsland_ddr4_32, ram_crux_ddr4_64, ram_teamforge_ddr4_32_red, ram_kingsland_rdimm5_32, ram_sorin_rdimm5_64, ram_crux_rdimm5_128, ram_kingsland_rdimm4_32, ssd_sorin_990pro_1tb, ssd_sorin_980_500, ssd_westline_sn850x_2tb, ssd_westline_sn850x_1tb_hs, ssd_westline_sn580_1tb, ssd_crux_p3plus_2tb, ssd_crux_t705_2tb_hs, ssd_crux_mx500_2tb, ssd_kingsland_a400_480, hdd_seacrest_2tb, hdd_westline_4tb, hdd_seacrest_8tb, hdd_seacrest_exos_20tb, ssd_sorin_pm9a3_3840, ssd_sorin_pm9a3_7680, psu_seastar_px1000_white, psu_corvex_rm850x_white, psu_hush_pp12m_750, psu_hush_dp13_1200, psu_mako_a850g, psu_aegis_1200p, psu_corvex_ax1600i, psu_corvex_sf750, psu_strata_crps_800, psu_strata_crps_1600, cooler_arctiq_34_black, cooler_arctiq_34_white, cooler_glacier_ak400_white, cooler_glacier_ak620_black, cooler_noctis_d15_black, cooler_frostpeak_120_rgb, cooler_arctiq_lc240, cooler_corvex_h150i_white, cooler_glacier_ls720, cooler_srv_epoch_1u, cooler_srv_platinum_2u, case_phanta_g360a, case_nexa_h5, case_facet_fjord, case_hush_500dx, case_facet_fizzair, case_brickhouse_beige98, fan_arctiq_p12_5pack, fan_noctis_a12x25, fan_noctis_a12x25_black, fan_lumin_sl120_white_3pack, fan_corvex_af120_rgb_3pack, fan_arctiq_p14, fan_hush_wing4_140, nic_linkwave_350t2, nic_linkwave_710da2, nic_melnet_strand6_25g, nic_melnet_strand6_100g, hba_broadline_9500_16i, hba_broadline_9560_16i, srv_strata_sg840_4u, srv_strata_sr224_2u, srv_linkwave_ls4804x, srv_linkwave_ls1600x, srv_strata_shelf_1u, srv_strata_blank_1u, srv_strata_blank_2u, srv_strata_cma, srv_strata_kvm_1u.

Built in this session (consumer parts of the existing box kinds); the server/OEM boxes, the rack gear and the new
consumer kinds (AIO, 3.5" HDD, fan packs, SFX PSU) are built by helper sessions on their own branches, each in its
own rig module, and merged in (their sections are below once merged).

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
| box_cpu_tiron_i3_14100 | | | | **not built yet** |
| box_cpu_tiron_i5_14600k | | | | **not built yet** |
| box_cpu_tiron_i7_14700 | | | | **not built yet** |
| box_cpu_tiron_i7_14700k | | | | **not built yet** |
| box_cpu_tiron_i9_14900k | | | | **not built yet** |

### Graphics cards
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_gpu_verdia_5060_zenith | 0.285 x 0.08 x 0.165 | 2062 | 8 | GPU: sleeve A_SLEEVE_0 (0) -> lid A_LID_0 (1) -> card in its silver bag A_ITEM_PART_0 (2, rests in the foam) -> PE foam cradle A_INSERT_FOAM_0 (3) -> 3 papers under the foam (4). |
| box_gpu_verdia_5060ti_aegis_white | | | | **not built yet** |
| box_gpu_verdia_5070_mako | | | | **not built yet** |
| box_gpu_verdia_5070ti_kestrel_white | | | | **not built yet** |
| box_gpu_verdia_5080_aegis | | | | **not built yet** |
| box_gpu_verdia_5090_ref | | | | **not built yet** |
| box_gpu_verdia_5090_mako | | | | **not built yet** |
| box_gpu_verdia_4060_kestrel_lp | | | | **not built yet** |
| box_gpu_voltra_7600_zenith | | | | **not built yet** |
| box_gpu_voltra_9060xt_zenith_white | | | | **not built yet** |
| box_gpu_voltra_9070xt_zenith | | | | **not built yet** |
| box_gpu_voltra_7900xtx_ref | | | | **not built yet** |
| box_gpu_tiron_b580_ref | | | | **not built yet** |

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
| box_ram_corvex_ddr5_32_black | 0.16 x 0.03 x 0.12 | 4350 | 11 | RAM: end tuck flap A_FLAP_0 (1) -> dust flaps A_FLAP_1/2 (2) -> blister tray A_INSERT_BLISTER_0 slides out +x (3), then on it: installation card A_ITEM_DOC_0 and the blister seal A_SEAL_0 (4) -> blister lid A_CLAMLID_0 (5) -> sticks A_ITEM_PART_0/1 (6, guard=1). |
| box_ram_corvex_ddr5_32_white_rgb | | | | **not built yet** |
| box_ram_gstride_ddr5_48_rgb | | | | **not built yet** |
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
| box_ram_kingsland_rdimm5_32 | | | | **not built yet** |
| box_ram_sorin_rdimm5_64 | | | | **not built yet** |
| box_ram_crux_rdimm5_128 | | | | **not built yet** |
| box_ram_kingsland_rdimm4_32 | | | | **not built yet** |

### Storage
| Box | Size (m) | Tris | Anchors | Opening sequence (order) |
|---|---|---|---|---|
| box_ssd_sorin_990pro_1tb | | | | **not built yet** |
| box_ssd_sorin_990pro_2tb_hs | 0.11 x 0.025 x 0.08 | 3284 | 10 | SSD M.2: seal A_SEAL_0 over the end flap's top edge (0) -> end flap A_FLAP_0 (1) -> dust flaps (2) -> blister A_INSERT_BLISTER_0 slides out +x (3) -> blister lid A_CLAMLID_0 and the 2 cards under the blister (4) -> SSD (5). |
| box_ssd_sorin_980_500 | | | | **not built yet** |
| box_ssd_westline_sn850x_2tb | | | | **not built yet** |
| box_ssd_westline_sn850x_1tb_hs | | | | **not built yet** |
| box_ssd_westline_sn580_1tb | | | | **not built yet** |
| box_ssd_crux_p3plus_2tb | | | | **not built yet** |
| box_ssd_crux_t705_2tb_hs | | | | **not built yet** |
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

## Deviations
- Paper kinds use the catalogue's names in `doc=` (`quick-start` is new next to guide, manual, warranty, sticker,
  driver, safety).

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

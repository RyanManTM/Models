# Catalogue 11: graphics cards (15)

**Status: all 15 ids done** (built, previews reviewed, committed). Shop data: `docs/catalog/gpus.json`.

Every card is `build_gpu.py`'s card with a new spec and its own style hooks, set up in `Tools/Blender/build_cat_gpus.py`.
The brand art (logo plate, hub sticker, serial label, series badge, colour swatches) is drawn there too, in the atlas
cells `build_gpu.build()` expects. Anchor report: `Logs/ModelPreviews/cat_gpus_report.txt`.

## Models

| id | name in the shop | size L x H x T (mm) | slots | fans | power anchor | tris | sibling |
|---|---|---|---|---|---|---|---|
| `gpu_verdia_5060_zenith` | Verdia VTX 5060 Duo 8 GB (Zenith) | 220 x 116 x 42 | 2 | 2 | `A_PORT_PCIE8_0` | 35 882 | rx66 |
| `gpu_verdia_5060ti_aegis_white` | Verdia VTX 5060 Ti Halo White 16 GB (Aegis) | 230 x 123 x 50 | 2.5 | 2 | `A_PORT_PCIE8_0` | 38 696 | rx66 |
| `gpu_verdia_5070_mako` | Verdia VTX 5070 Gale 3X 12 GB (Mako) | 288 x 115 x 50 | 2.5 | 3 | `A_PORT_PCIE8_0` | 47 388 | rx66 |
| `gpu_verdia_5070ti_kestrel_white` | Verdia VTX 5070 Ti Talon Ice 16 GB (Kestrel) | 304 x 126 x 50 | 2.5 | 3 | `A_PORT_12V2X6_0` | 50 912 | rx88 |
| `gpu_verdia_5080_aegis` | Verdia VTX 5080 Paladin 16 GB (Aegis) | 348 x 149 x 70 | 3.5 | 3 | `A_PORT_12V2X6_0` | 80 626 | rx88 |
| `gpu_verdia_5090_ref` | Verdia VTX 5090 Reference 32 GB | 304 x 137 x 40 | 2 | 2 | `A_PORT_12V2X6_0` | 42 828 | rx88 |
| `gpu_verdia_5090_mako` | Verdia VTX 5090 Leviathan 32 GB (Mako) | 359 x 150 x 80 | 4 | 3 | `A_PORT_12V2X6_0` | 84 448 | rx88 |
| `gpu_verdia_4060_kestrel_lp` | Verdia VTX 4060 Low Profile 8 GB (Kestrel) | 182 x 69 x 40 | 2 | 2 | `A_PORT_PCIE8_0` | 35 970 | rx66 |
| `gpu_voltra_7600_zenith` | Voltra RX 7600 Core 8 GB (Zenith) | 240 x 120 x 43 | 2 | 2 | `A_PORT_PCIE8_0` | 36 568 | rx66 |
| `gpu_voltra_9060xt_zenith_white` | Voltra RX 9060 XT Frost White 16 GB (Zenith) | 245 x 120 x 45 | 2 | 2 | `A_PORT_PCIE8_0` | 37 964 | rx66 |
| `gpu_voltra_9070xt_zenith` | Voltra RX 9070 XT Flare+ 16 GB (Zenith) | 320 x 128 x 62 | 3 | 3 | `A_PORT_12V2X6_0` | 69 478 | rx88 |
| `gpu_voltra_7900xtx_ref` | Voltra RX 7900 XTX Reference 24 GB | 287 x 123 x 51 | 2.5 | 3 | `A_PORT_PCIE8_0..1` | 56 520 | rx77 |
| `gpu_tiron_b580_ref` | Tiron Lumen B580 Reference 12 GB | 272 x 115 x 45 | 2 | 2 | `A_PORT_PCIE8_0` | 40 716 | rx66 |
| `gpu_verdia_t100` | Verdia T100 80 GB PCIe (data centre) | 268 x 111 x 40 | 2 | 0 | `A_PORT_12V2X6_0` | 30 618 | rx88 (new contract) |
| `gpu_voltra_mi210` | Voltra Vector MI210 64 GB (data centre) | 267 x 111 x 40 | 2 | 0 | `A_PORT_PCIE8_0` | 30 416 | rx66 (new contract) |

Looks, by brand (each card has its own overlay, skirts, logo plate, trim and backplate hooks):
- **Zenith** (Zotac / Sapphire): Duo (compact black, grey corner panels, silver slashes), Core (plain black, raised
  dark bands, no RGB), Frost (white, grey inlays, white fans), Flare+ (gunmetal metal face, ARGB blades between the
  fans and a slanted ARGB bar, ARGB on the top edge, 3 slots).
- **Aegis** (ASUS): Halo White (white, the slashed grey divider, silver edge lines, a small ARGB strip); Paladin
  (black faceted dark metal, the big slanted ARGB light bar at the far end, an ARGB prism on the top edge, 3.5 slots).
- **Mako** (MSI): Gale 3X (black with silver claws between the fans, no RGB); Leviathan (a brushed silver frame round
  a black face, ARGB lines along the frame and on the top edge, 4 slots).
- **Kestrel** (Gigabyte): Talon Ice (white, silver wedge corners, X-cuts, ARGB logo strip); Low Profile (half height).
- **Verdia reference**: a 2-slot double flow-through card, dark face in a silver frame with a silver spine, the
  lit (white LED) logo.
- **Voltra reference**: gunmetal, silver chamfered edges, the three red stripes, silver rings.
- **Tiron reference**: matte black, silver frame round the face and edges, no RGB.

The backplates have flow-through windows past the PCB end (slats, hex or an open window, with the fin stack grown up
to the backplate behind them) where the real card has one, the brand print and the serial label.

## Contract and anchor comparison (desktop cards)

Same frame and anchor kinds as gpu_rx66 / rx77 / rx88: the PCIe edge at the origin, the full-height bracket at
x +0.095, the cooler facing -y, the height along +z. `anchor_compare.py` against the sibling in the table above:

| anchors | result on all 13 desktop cards |
|---|---|
| `A_PORT_DP_0..2`, `A_PORT_HDMI_0` | SAME |
| `A_SCREW_PH2_0..1` (bracket screws) | SAME |
| `A_HIT_1` (bracket), `A_HIT_2` (PCIe edge) | SAME |
| `A_PORT_PCIE8_0..1` / `A_PORT_12V2X6_0` | same kind, size and meta; position along the top edge (x) and z = PCB height + 4 mm differ (free) |
| `A_FAN_0..n` | same kind and meta (rpm differs); count, diameter and position differ (free) |
| `A_HIT_0`, `A_FILM_BACKPLATE_0`, `A_FILM_SHROUD_0` | same kind and meta; size and position follow the card's size (free) |

Summary lines: 8 SAME on every desktop card (the eight fixed anchors), the rest DIFF only in position/size;
`gpu_verdia_5070_mako` vs rx66 has the extra `A_FAN_2`, `gpu_verdia_5090_ref` vs rx88 lacks `A_FAN_2` (2 fans).

## New contract: passive data-centre accelerators (`contract: "gpu_dc"`, `new_contract: true`)

`gpu_verdia_t100` (an H100-PCIe-style card) and `gpu_voltra_mi210`:
- **Frame:** exactly the desktop card's (PCIe edge at the origin, full-height bracket at x +0.095, the closed shroud
  face at -y, height along +z). Dual slot (40 mm).
- **Anchors:** `A_SCREW_PH2_0..1`, `A_HIT_1`, `A_HIT_2` SAME as the desktop cards; `A_HIT_0`, `A_FILM_BACKPLATE_0`,
  `A_FILM_SHROUD_0` (the film on the top-edge name plate) as on them; the power port at the far end of the top edge,
  facing +z: `A_PORT_12V2X6_0` (T100, x -0.148) or `A_PORT_PCIE8_0` (MI210, x -0.147).
- **No `A_PORT_DP_*` / `A_PORT_HDMI_0`** (no display outputs: the bracket is a solid hex-vented exhaust grille) and
  **no `A_FAN_n`** (passive: the fins reach the face plate, the far end is a hex intake grille).
- **Game support needed:** the card needs server airflow front to back (through the far-end grille, out of the
  bracket). In a desktop case it should overheat, or the game should only allow it in a server chassis. It shouldn't
  count as a display adapter.

## Deviations
- **Output mix:** every desktop card keeps the contract's 3 x DP + 1 x HDMI at the rx66 positions. The real
  RX 7900 XTX reference has 2 x DP + 1 x USB-C + 1 x HDMI, and the real Gigabyte 4060 Low Profile has 2 x DP + 2 x HDMI.
- **Low profile (`gpu_verdia_4060_kestrel_lp`):** ships with the full-height bracket fitted (contract kept); its ports
  above the 64 mm PCB sit on a small riser board. The box also holds a half-height bracket (for the game/box task:
  not modelled; a later `bracket_lp` part could carry it).
- **Thick cards (3, 3.5, 4 slots):** the bracket plate grows over the extra slots (vented, looks only). The screws and
  `A_HIT_1` stay on the two-slot tab, so the game still sees a two-slot bracket; it should block the slot covers below.
- **Power positions:** the game supports one 12V-2x6 or one or two 8-pins. Real power positions differ (the 9070 XT
  Nitro+ hides its 12V-2x6 under the backplate, the H100 PCIe and MI210 take power at the rear end face); all are on
  the top edge, facing +z, like the siblings.
- **MI210 power:** the real card has an 8-pin EPS (CPU) socket; it is modelled and listed as a PCIe 8-pin
  (`PCIe8x1`), the plug the game has.
- **Names:** "Instinct" is AMD's trademark, so the MI210 analog is the "Voltra Vector MI210". Partner series names are
  invented (Duo, Halo, Gale 3X, Talon Ice, Paladin, Leviathan, Core, Frost, Flare+).
- **Fans:** the 40-42 mm cards (5060, 5090 ref, 4060 LP) have 13 mm fans as all `build_gpu` cards; on the
  40 mm cards the heat pipes come within 1 mm of the fan blades (not visible).
- The 5080 Paladin's real analog (ROG Astral) has a fourth fan on the backplate side; this one has three, per the brief.

## Hooks added to `build_gpu.py` (optional, no-op on existing cards)
`texture`, `brand`, `outputs: False`, `fans: 0`, `fan_kw`, `fan_rpm`, `vent: "full"`, and a `logo` hook may return
`rgb_x None`. Proof: `gpu_rx66`, `gpu_rx88` (build_gpu.py) and `gpu_rx77` (build_parts_d.py) were re-exported on Linux
with the old and the new script into scratch folders: `extras_compare.py` says **SAME** for all three (37, 38 and 38
objects). Those re-exports are not committed.

## Rebuild
```
blender -b --factory-startup -P Tools/Blender/build_cat_gpus.py -- [ids...] [--nopreview]
```
With no ids it builds all 15 (about 10 minutes with previews). Built on Linux with the bpy 5.0.1 module.

## README line
`build_cat_gpus.py` | Catalogue 11: 15 graphics cards (13 desktop: Verdia VTX 5060-5090, 4060 LP, Voltra RX 7600-9070 XT, 7900 XTX, Tiron Lumen B580; 2 passive data-centre accelerators), build_gpu.py specs with brand style hooks

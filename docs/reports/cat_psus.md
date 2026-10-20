# Catalogue 15: power supplies — report

Thirteen PSUs (10 desktop ATX, 1 SFX, 2 server CRPS) plus the SFX-to-ATX bracket that ships with the SFX unit.
**Status: all 13 ids done.** Catalogue data: `docs/catalog/psus.json`.

| Group | ids | status |
|---|---|---|
| Desktop ATX (10) | psu_ampere_550_bronze, psu_corvex_cx650m, psu_seastar_gx850, psu_seastar_px1000_white, psu_corvex_rm850x_white, psu_hush_pp12m_750, psu_hush_dp13_1200, psu_mako_a850g, psu_aegis_1200p, psu_corvex_ax1600i | done |
| SFX (1) | psu_corvex_sf750 (+ psu_bracket_sfx_atx) | done |
| Server CRPS (2) | psu_strata_crps_800, psu_strata_crps_1600 | done |

## Rebuild

```bash
blender -b --factory-startup -P Tools/Blender/build_cat_psus.py -- [ids...] [--nopreview]
```

No ids builds everything. Each id writes `Assets/Resources/Models/<id>.fbx`, `Models/Textures/<id>.png`
(one atlas per unit; the bracket has none), `Logs/ModelPreviews/<id>_<n>.png` and `<id>_report.txt`; every run also
rewrites `docs/catalog/psus.json` and `Logs/ModelPreviews/cat_psus_report.txt` (all the per-id reports in one file).
Built in the cloud with Blender 5.0.1 as the `bpy` module (Python 3.11).

**Files:** `Tools/Blender/build_cat_psus.py` (specs, the parametric ATX/SFX builder, the bracket, the CRPS builder,
the JSON) and `Tools/Blender/cat_psus_art.py` (label/hub/panel/OLED artwork, brand marks drawn from shapes).
**`build_psu.py` is not changed** — the new script imports its rear-face constants (`SCREWS`, `INLET`, `SWITCH`) and
its `socket()` helper — so psu_450 / psu_750 are untouched and need no SAME proof.

## Models

| id | name | W | tier | contract | size (w×h×d mm) | tris | meshes | eps8/pcie8/12V-2x6/sata | modular | price |
|---|---|---|---|---|---|---|---|---|---|---|
| `psu_ampere_550_bronze` | Ampere BP-550 550 W Bronze | 550 | Bronze | psu | 150×86×140 | 33912 | 18 | 1/2/0/6 | none | $49 |
| `psu_corvex_cx650m` | Corvex CX650M 650 W Bronze | 650 | Bronze | psu | 150×86×140 | 33762 | 20 | 1/4/0/8 | semi | $75 |
| `psu_seastar_gx850` | Seastar Apex GX-850 850 W Gold | 850 | Gold | psu | 150×86×140 | 36692 | 18 | 2/6/0/10 | full | $130 |
| `psu_seastar_px1000_white` | Seastar Summit PX-1000 1000 W Platinum White | 1000 | Platinum | psu | 150×86×160 | 35234 | 17 | 2/4/1/8 | full | $230 |
| `psu_corvex_rm850x_white` | Corvex RM850x 850 W Gold White | 850 | Gold | psu | 150×86×160 | 39626 | 17 | 3/4/1/14 | full | $140 |
| `psu_hush_pp12m_750` | Hush Clean Power 12 M 750 W Gold | 750 | Gold | psu | 150×86×160 | 34124 | 18 | 2/2/1/6 | full | $100 |
| `psu_hush_dp13_1200` | Hush Shadow Power 13 1200 W Titanium | 1200 | Titanium | psu | 150×86×175 | 43094 | 19 | 2/6/1/12 | full | $330 |
| `psu_mako_a850g` | Mako Forge A850G PCIE5 850 W Gold | 850 | Gold | psu | 150×86×140 | 35722 | 18 | 2/4/1/8 | full | $120 |
| `psu_aegis_1200p` | Aegis Valkyr 1200P 1200 W Platinum | 1200 | Platinum | psu | 150×86×190 | 37924 | 20 | 2/6/1/12 | full | $330 |
| `psu_corvex_ax1600i` | Corvex AX1600i 1600 W Titanium | 1600 | Titanium | psu | 150×86×200 | 46024 | 19 | 2/10/0/16 | full | $580 |
| `psu_corvex_sf750` | Corvex SF750 750 W Platinum SFX | 750 | Platinum | psu_sfx | 125×63.5×100 | 39918 | 18 | 2/4/0/8 | full | $180 |
| `psu_strata_crps_800` | Strata 800 W Platinum CRPS Hot-Plug PSU | 800 | Platinum | psu_crps | 73.5×40×185 | 10778 | 15 | 0/0/0/0 | crps | $150 |
| `psu_strata_crps_1600` | Strata 1600 W Titanium CRPS Hot-Plug PSU | 1600 | Titanium | psu_crps | 73.5×40×185 | 10778 | 15 | 0/0/0/0 | crps | $320 |
| `psu_bracket_sfx_atx` | SFX-to-ATX bracket (in the SF750 box) | – | – | psu (ATX frame) | 150×86×24 | 1920 | 2 | – | – | – |

Anchor comparison (`anchor_compare.py`, sibling → new model). Rear face = A_SWITCH_PSU_0, A_PORT_C13_0, A_SCREW_PH2_0..3.

| id | sibling | SAME | DIFF | ONLY sibling | ONLY new | rear face |
|---|---|---|---|---|---|---|
| `psu_aegis_1200p` | psu_750 | 6 | 11 | 0 | 7 | all 6 SAME |
| `psu_ampere_550_bronze` | psu_450 | 8 | 1 | 0 | 0 | all 6 SAME |
| `psu_bracket_sfx_atx` | psu_450 | 0 | 5 | 4 | 5 | screws SAME (meta +into=case) |
| `psu_corvex_ax1600i` | psu_750 | 6 | 10 | 1 | 12 | all 6 SAME |
| `psu_corvex_cx650m` | psu_450 | 8 | 1 | 0 | 5 | all 6 SAME |
| `psu_corvex_rm850x_white` | psu_750 | 6 | 11 | 0 | 4 | all 6 SAME |
| `psu_corvex_sf750` | psu_750 | 0 | 15 | 2 | 1 | new SFX rear (see below) |
| `psu_hush_dp13_1200` | psu_750 | 6 | 11 | 0 | 5 | all 6 SAME |
| `psu_hush_pp12m_750` | psu_750 | 6 | 10 | 1 | 0 | all 6 SAME |
| `psu_mako_a850g` | psu_750 | 8 | 9 | 0 | 3 | all 6 SAME |
| `psu_seastar_gx850` | psu_750 | 7 | 9 | 1 | 4 | all 6 SAME |
| `psu_seastar_px1000_white` | psu_750 | 6 | 11 | 0 | 3 | all 6 SAME |

All ATX/SFX units: `A_FAN_0` rotor, `A_SWITCH_PSU_0` rocker (moving pieces), `A_PORT_C13_0` (the C14 inlet, kept
under the psu_450 name), `A_SCREW_PH2_0..3`, `A_HIT_0`; non-modular `A_CABLE_EXIT_0`; modular `A_PORT_MOD_*`.
The per-anchor tables with positions, axes, sizes and meta are in `Logs/ModelPreviews/<id>_report.txt`.

**Anchor DIFFs are expected:** `A_PORT_MOD_*` move because every unit has its own panel layout (and longer units
have the front face further towards −x), their meta gains `feeds=`; `A_FAN_0` and `A_HIT_0` follow the box centre
of longer units; `A_CABLE_EXIT_0` meta lists the real bundle. The six rear-face anchors are SAME on all ten ATX units.

### Looks per unit
- **Ampere 550 Bronze** – black, wire grille, sleeved fixed bundle, bronze badge.
- **Corvex CX650M** – black; fixed 24-pin + EPS bundle through a grommet at the left of the front face, a
  modular panel for 2 PCIe and 3 SATA/peripheral sockets on the right; dark label with the sail mark.
- **Seastar GX-850** – black, stamped hexagonal grille, navy/white label, star mark.
- **Seastar PX-1000 White** – white, concentric-slot grille, white fan, ATX 3.1, 12V-2x6 socket, platinum badge.
- **Corvex RM850x White** – white, hex grille, white fan, 3 CPU sockets, 12V-2x6.
- **Hush Clean Power 12 M** – black with brushed silver stripes along both sides, wire grille, orange accents.
- **Hush Shadow Power 13 1200** – black, wire grille with a brushed aluminium fan ring, aluminium side plate, titanium badge, 175 mm.
- **Mako A850G** – black, concentric-slot grille with a red trim ring, 12V-2x6, red/black label.
- **Aegis Valkyr 1200P** – 190 mm; on the window side (+z) an angular dark-aluminium armour plate with a diagonal
  ARGB bar and edge line (`rgb` tag, `A_RGB_0`) and an OLED wattage read-out (`A_SCREEN_0`); label moved to −z.
- **Corvex AX1600i** – 200 mm, hex grille, 140 mm fan, aluminium side plate, 12 eight-pin sockets.
- **Corvex SF750** – SFX, 92 mm fan behind a round-hole perforated plate.
- **Strata CRPS 800 / 1600** – bare aluminium / dark steel tube body, top label, hex fan grille, vertical C14,
  black pull handle, orange (800) or blue (1600) latch tab, gold card edge.

## Contracts

### ATX (`psu`, as psu_450 / psu_750)
Frame unchanged: origin at the box centre of the 140 mm unit; x = depth (rear face at +0.07), y = height 0.086
(fan at −y), z = width 0.15. **Longer units (160–200 mm) keep the rear face at +0.07 and grow towards −x**: the front
face is at `0.07 − depth`, so they fit `A_SOCKET_PSU_0` from the rear exactly like psu_450 (cases with a short bay
would need a depth check: `specs.depth_mm`).
- **Modular sockets:** `A_PORT_MOD_ATX_0`, `A_PORT_MOD_CPU_<i>`, `A_PORT_MOD_PCIE_<i>`, `A_PORT_MOD_12V2X6_<i>`,
  `A_PORT_MOD_SATA_<i>` on the −x face (forward −x, latch +y). New meta key `feeds=<n>`: how many connectors the
  cable from that socket carries (daisy chains, SATA strings). The sum of `feeds` per kind equals the game counts.
- **Semi-modular (CX650M):** `A_CABLE_EXIT_0` (meta `bundle=atx24,eps8`) for the fixed cables, plus
  `A_PORT_MOD_PCIE_*` / `A_PORT_MOD_SATA_*`. In the JSON `psu_modular` is false (it is a bool) and
  `specs.modular` says `semi`; the game can tell from the anchors.
- **Game counts** (`psu_eps8`, `psu_pcie8`, `psu_16`, `psu_sata`) are connectors on the cables (EPS 4+4,
  PCIe 6+2, 12V-2x6, SATA power plugs), taken from the real units' spec sheets as best known.
- Extra anchors on the Aegis: `A_SCREEN_0` (OLED face centre, forward +z, size = visible area 38 × 13.5 mm, meta
  `kind=oled,res=128x48,shows=watts`) and `A_RGB_0` (the ARGB zone, `kind=argb,zones=2`).

### SFX (`psu_sfx`, new) — psu_corvex_sf750
- **Frame:** origin at the box centre; x = depth 0.100 with the rear face at **+0.050**; y = height 0.0635 with the
  92 mm fan at −y; z = width 0.125. Same anchor kinds and meta as ATX.
- **Rear face:** `A_PORT_C13_0` at (0.0514, −0.0045, 0.033), `A_SWITCH_PSU_0` at (0.0504, 0.0185, 0.033),
  `A_SCREW_PH2_0..3` at (0.05, ±0.0255, −0.0565 / +0.0565 / −0.0565 / +0.0405) (the SFX rear screw pattern).
- Modular panel on −x (`A_PORT_MOD_*` at x −0.0504).
- **SFX-to-ATX bracket `psu_bracket_sfx_atx`:** a separate model in the **ATX PSU frame**, so it drops on the case's
  `A_SOCKET_PSU_0` like any ATX unit. `A_SCREW_PH2_0..3` are the ATX screw holes (same positions as psu_450, meta
  `into=case`); `A_SOCKET_PSU_SFX_0` at (0.0188, −0.0113, −0.0075) is the pose of the SFX unit's origin (it sits
  on the bracket's bottom shelf, its rear face against the plate, fan down); `A_SCREW_PH2_4..7` (meta `into=sfx`)
  are the four screws through the plate into the SFX unit's rear holes. Game flow: install bracket → slide SFX in →
  4 SFX screws; or screw the bracket to the SFX first and install the pair as one ATX unit.

### CRPS (`psu_crps`, new) — psu_strata_crps_800 / _1600
- **Frame:** origin at the body centre; x = depth 0.185 with the rear (handle, inlet, fan, LED) at **+0.0925** and the
  card edge at −x; y = height 0.040 (label on top, +y); z = width 0.0735 (latch on +z).
- **Anchors:**
  - `A_PORT_EDGE_0` (−0.1025, −0.008, 0): the tip of the gold card edge that plugs into the server's power
    distribution board; forward −x (the server's connector comes from −x). Meta `kind=crps_card_edge,pads=2x26`.
    The server's PSU bay gets a matching `A_SOCKET_CRPS_<n>` = this pose when fully inserted; insertion is along +x.
  - `A_PORT_C14_0` (0.0911, 0.001, 0.019): vertical C14 inlet, forward +x (meta `key=+z,vertical=1`).
  - `A_HANDLE_0` (0.1185, 0, 0.0315): the pull handle (moving piece `handle`/`grip`, fixed; it is the grab point,
    `dir=+x`).
  - `A_LATCH_0` (0.0985, −0.0125, 0.0347): the release tab (moving piece), `press=-z,travel=0.002`: pressed
    towards −z it frees the module from the cage.
  - `A_LED_STATUS_0` (0.0897, 0.015, 0.0305): bi-colour status LED (`led_green` mesh; meta `colors=green,amber`).
  - `A_FAN_0` (40 mm class rotor, 32 mm modelled, forward +x, 12000 rpm), `A_HIT_0`.
- Game data: `psu_watts`, `psu_efficiency`; all connector counts 0 (power goes through the card edge).
  `category` = Server.

## Deviations
- The ATX inlet anchor keeps the existing name `A_PORT_C13_0` (as psu_450/psu_750) so the ATX contract stays
  identical; the CRPS uses `A_PORT_C14_0` as the brief asks.
- `power_w` is 0 for all PSUs (they supply power; the wattage is `game.psu_watts`).
- Corsair/Seasonic/MSI-style model numbers (CX650M, RM850x, AX1600i, SF750, GX-850, PX-1000, A850G) are kept as the
  numbering scheme; trademarked series words were replaced: Focus → Apex, Vertex → Summit, Pure Power → Clean Power,
  Dark Power → Shadow Power, MPG → Forge, ROG Thor → Valkyr.
- The CRPS fan is modelled at 32 mm (real modules use 40 mm fans in a 40 mm-tall body; the folded body leaves 38 mm).
- Connector counts are best-known spec-sheet values of the analogues (some revisions differ by a SATA or PCIe plug).
- Panel and label text is small but legible at bench distance; the brand marks are simple invented shapes.

## README line
| `build_cat_psus.py` | Catalogue 15: 13 PSUs (10 ATX, SFX `psu_corvex_sf750` + `psu_bracket_sfx_atx`, 2 CRPS server modules) and `docs/catalog/psus.json`; reuses `build_psu.py`'s rear face and sockets, art in `cat_psus_art.py` |
